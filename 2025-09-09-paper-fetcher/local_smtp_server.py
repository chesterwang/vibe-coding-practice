#!/usr/bin/env python3
"""
Local SMTP Server for testing email functionality
Creates a temporary SMTP server that saves emails to files instead of sending them
"""

import socket
import threading
import time
import os
from datetime import datetime
import email
import logging

logger = logging.getLogger(__name__)

class LocalSMTPServer:
    """Simple local SMTP server that saves emails to files"""
    
    def __init__(self, host='localhost', port=1025, output_dir="emails"):
        self.host = host
        self.port = port
        self.output_dir = output_dir
        self.running = False
        self.server_socket = None
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Local SMTP server initialized on {host}:{port}")
        logger.info(f"Emails will be saved to: {os.path.abspath(output_dir)}")
    
    def handle_client(self, client_socket, client_address):
        """Handle SMTP client connection"""
        try:
            # Send greeting
            client_socket.send(b"220 localhost SMTP Server Ready\r\n")
            
            mail_from = ""
            rcpt_to = []
            data_mode = False
            email_data = b""
            
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    command = data.decode('utf-8', errors='ignore').strip()
                    
                    if data_mode:
                        if command == ".":
                            # End of email data
                            data_mode = False
                            self.save_email(mail_from, rcpt_to, email_data)
                            client_socket.send(b"250 Message accepted\r\n")
                            email_data = b""
                            mail_from = ""
                            rcpt_to = []
                        else:
                            email_data += data
                    else:
                        # Parse SMTP commands
                        if command.upper().startswith("HELO") or command.upper().startswith("EHLO"):
                            client_socket.send(b"250 Hello\r\n")
                        elif command.upper().startswith("MAIL FROM:"):
                            mail_from = command[10:].strip().strip('<>')
                            client_socket.send(b"250 OK\r\n")
                        elif command.upper().startswith("RCPT TO:"):
                            rcpt_to.append(command[8:].strip().strip('<>'))
                            client_socket.send(b"250 OK\r\n")
                        elif command.upper() == "DATA":
                            client_socket.send(b"354 Start mail input; end with <CRLF>.<CRLF>\r\n")
                            data_mode = True
                        elif command.upper() == "QUIT":
                            client_socket.send(b"221 Bye\r\n")
                            break
                        else:
                            client_socket.send(b"250 OK\r\n")
                            
                except Exception as e:
                    logger.error(f"Error handling client command: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
    
    def save_email(self, mail_from, rcpt_to, email_data):
        """Save email to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f"email_{timestamp}.eml"
            filepath = os.path.join(self.output_dir, filename)
            
            # Save raw email
            with open(filepath, 'wb') as f:
                f.write(email_data)
            
            # Parse email for summary
            try:
                msg = email.message_from_bytes(email_data)
                subject = msg.get('Subject', 'No Subject')
            except:
                subject = 'Parse Error'
            
            # Create readable summary
            summary_file = filepath.replace('.eml', '_summary.txt')
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"Email Summary\n")
                f.write(f"=" * 50 + "\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"From: {mail_from}\n")
                f.write(f"To: {', '.join(rcpt_to)}\n")
                f.write(f"Subject: {subject}\n")
                f.write(f"Raw file: {filename}\n")
                f.write(f"\nContent Preview:\n")
                f.write("-" * 30 + "\n")
                
                # Extract text content
                try:
                    msg = email.message_from_bytes(email_data)
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                content = part.get_payload(decode=True)
                                if content:
                                    try:
                                        text_content = content.decode('utf-8')[:1000]
                                        f.write(text_content)
                                        if len(content) > 1000:
                                            f.write("\n... (truncated)")
                                    except:
                                        f.write("(Binary or unreadable content)")
                                break
                    else:
                        content = msg.get_payload(decode=True)
                        if content:
                            try:
                                text_content = content.decode('utf-8')[:1000]
                                f.write(text_content)
                                if len(content) > 1000:
                                    f.write("\n... (truncated)")
                            except:
                                f.write("(Binary or unreadable content)")
                except Exception as e:
                    f.write(f"Error parsing email: {e}")
            
            logger.info(f"Email received and saved: {filename}")
            logger.info(f"Subject: {subject}")
            logger.info(f"From: {mail_from} To: {', '.join(rcpt_to)}")
            
            print(f"\n📧 Email received!")
            print(f"Subject: {subject}")
            print(f"From: {mail_from}")
            print(f"To: {', '.join(rcpt_to)}")
            print(f"Saved to: {filepath}")
            print(f"Summary: {summary_file}")
            
        except Exception as e:
            logger.error(f"Error saving email: {e}")
    
    def start(self):
        """Start the SMTP server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            logger.info(f"SMTP server listening on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connection: {e}")
                    
        except Exception as e:
            logger.error(f"Error starting SMTP server: {e}")
            self.running = False
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def stop(self):
        """Stop the SMTP server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

class SMTPServerManager:
    """Manager for the local SMTP server"""
    
    def __init__(self, host='localhost', port=1025, output_dir="emails"):
        self.host = host
        self.port = port
        self.output_dir = output_dir
        self.server = None
        self.server_thread = None
        self.running = False
    
    def start(self):
        """Start the SMTP server in a separate thread"""
        if self.running:
            logger.warning("SMTP server is already running")
            return True
        
        try:
            self.server = LocalSMTPServer(self.host, self.port, self.output_dir)
            
            def run_server():
                try:
                    self.server.start()
                except Exception as e:
                    logger.error(f"SMTP server error: {e}")
                    self.running = False
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            self.running = True
            
            # Give server time to start
            time.sleep(0.5)
            
            logger.info(f"SMTP server started on {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start SMTP server: {e}")
            self.running = False
            return False
    
    def stop(self):
        """Stop the SMTP server"""
        if not self.running:
            return
        
        try:
            if self.server:
                self.server.stop()
            self.running = False
            logger.info("SMTP server stopped")
        except Exception as e:
            logger.error(f"Error stopping SMTP server: {e}")
    
    def is_running(self):
        """Check if server is running"""
        return self.running
    
    def get_config(self):
        """Get configuration for email client"""
        return {
            "smtp_server": self.host,
            "smtp_port": self.port,
            "sender_email": "test@localhost",
            "sender_password": "",  # No password needed for local server
            "use_tls": False
        }

def main():
    """Run the local SMTP server standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Local SMTP Server for testing')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=1025, help='Server port')
    parser.add_argument('--output', default='emails', help='Output directory for emails')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print(f"Starting local SMTP server on {args.host}:{args.port}")
    print(f"Emails will be saved to: {os.path.abspath(args.output)}")
    print("Press Ctrl+C to stop the server")
    
    server_manager = SMTPServerManager(args.host, args.port, args.output)
    
    try:
        if server_manager.start():
            print("✅ Server started successfully!")
            print(f"Configure your email client to use: {args.host}:{args.port}")
            print("No authentication required")
            
            # Keep server running
            while server_manager.is_running():
                time.sleep(1)
        else:
            print("❌ Failed to start server")
            
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server_manager.stop()
        print("Server stopped")

if __name__ == "__main__":
    main()
