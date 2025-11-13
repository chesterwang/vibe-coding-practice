// ====== 文件: background.js (插件核心逻辑) ======
// 这个脚本作为Service Worker运行，处理插件图标的点击事件。

// 监听插件图标的点击事件
chrome.action.onClicked.addListener(async (tab) => {
  // 获取当前活跃标签页的URL
  const currentUrl = tab.url;

  // 检查URL是否为GitHub仓库页面
  if (isGithubRepoUrl(currentUrl)) {
    // 如果是，则开始提取和合并Markdown文件
    const { owner, repo } = getRepoInfoFromUrl(currentUrl);
    try {
      // 递归获取仓库中所有文件
      const allFiles = await fetchRepoContents(owner, repo);
      // 过滤出所有Markdown文件
      const markdownFiles = allFiles.filter(file => file.path.endsWith('.md') || file.path.endsWith('.markdown'));

      if (markdownFiles.length === 0) {
        // 如果没有找到Markdown文件，则显示提示信息
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          function: displayMessage,
          args: ["该仓库没有找到Markdown文件。"]
        });
        return;
      }
      
      // 提取并合并所有Markdown文件的内容
      const combinedMarkdown = await combineMarkdownFiles(owner, repo, markdownFiles);
      
      // 创建新标签页显示合并后的Markdown内容
      await displayMarkdownInNewTab(combinedMarkdown);

    } catch (error) {
      console.error('发生错误:', error);
      let errorMessage = "无法访问或合并仓库内容。可能的原因：\n1. 网络连接问题。\n2. GitHub API请求次数已达限制（未登录状态下）。\n3. 仓库不存在或为私有。";
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: displayMessage,
        args: [errorMessage]
      });
    }

  } else {
    // 如果不是GitHub仓库页面，则显示不支持的信息
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: displayMessage,
      args: ["该页面暂不支持Markdown合并。"]
    });
  }
});

/**
 * 检查一个URL是否是GitHub仓库页面。
 * @param {string} url - 待检查的URL。
 * @returns {boolean} - 如果是GitHub仓库页面则返回true。
 */
function isGithubRepoUrl(url) {
  const repoRegex = /^https:\/\/github\.com\/[^\/]+\/[^\/]+(\/|$)/;
  return repoRegex.test(url);
}

/**
 * 从GitHub仓库URL中提取所有者和仓库名称。
 * @param {string} url - GitHub仓库的URL。
 * @returns {{owner: string, repo: string}} - 包含所有者和仓库名称的对象。
 */
function getRepoInfoFromUrl(url) {
  const parts = url.split('/').filter(p => p !== '');
  const owner = parts[3];
  const repo = parts[4];
  return { owner, repo };
}

/**
 * 递归获取GitHub仓库中所有文件的路径。
 * @param {string} owner - 仓库所有者。
 * @param {string} repo - 仓库名称。
 * @param {string} [path=''] - 文件夹路径，默认为根目录。
 * @param {Object} [options] - 配置选项
 * @param {number} [options.maxRetries=3] - 最大重试次数
 * @param {number} [options.retryDelay=1000] - 重试延迟（毫秒）
 * @param {AbortSignal} [options.signal] - 用于取消请求的AbortSignal
 * @returns {Promise<Array<{path: string, type: string}>>} - 包含所有文件路径和类型（file/dir）的数组。
 */
async function fetchRepoContents(owner, repo, path = '', options = {}) {
  const { maxRetries = 3, retryDelay = 1000, signal } = options;
  
  // 输入验证
  if (!owner || !repo) {
    throw new Error('仓库所有者和仓库名称不能为空');
  }

  const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${path}`;
  
  // 带重试机制的fetch
  const fetchWithRetry = async (url, attempt = 1) => {
    try {
      const response = await fetch(url, {
        signal,
        headers: {
          'Accept': 'application/vnd.github.v3+json',
          'User-Agent': 'Chrome-Extension-Markdown-Merger'
        }
      });

      // 处理速率限制
      if (response.status === 403 && response.headers.get('X-RateLimit-Remaining') === '0') {
        const resetTime = response.headers.get('X-RateLimit-Reset');
        const waitTime = resetTime ? (parseInt(resetTime) * 1000) - Date.now() : 60000;
        throw new Error(`API速率限制，请等待 ${Math.ceil(waitTime / 1000)} 秒后重试`);
      }

      if (!response.ok) {
        throw new Error(`GitHub API错误: ${response.status} ${response.statusText}`);
      }

      return response;
    } catch (error) {
      if (attempt < maxRetries && error.name !== 'AbortError') {
        console.warn(`请求失败，${retryDelay}ms后重试 (${attempt}/${maxRetries}):`, error.message);
        await new Promise(resolve => setTimeout(resolve, retryDelay * attempt));
        return fetchWithRetry(url, attempt + 1);
      }
      throw error;
    }
  };

  try {
    const response = await fetchWithRetry(apiUrl);
    const items = await response.json();

    // 验证响应格式
    if (!Array.isArray(items)) {
      throw new Error('无效的API响应格式');
    }

    // 使用Promise.all并行处理目录，提高性能
    const filePromises = items.map(async (item) => {
      if (item.type === 'file') {
        return [{ path: item.path, type: 'file' }];
      } else if (item.type === 'dir') {
        // 并行递归获取子目录内容
        return fetchRepoContents(owner, repo, item.path, options);
      }
      return [];
    });

    // 使用flatMap模式避免多次数组拼接
    const results = await Promise.all(filePromises);
    return results.flat();
    
  } catch (error) {
    // 提供更详细的错误信息
    if (error.name === 'AbortError') {
      throw new Error('请求被取消');
    }
    throw new Error(`获取仓库内容失败: ${error.message}`);
  }
}

/**
 * 使用缓存机制获取仓库内容
 * @param {string} owner - 仓库所有者
 * @param {string} repo - 仓库名称
 * @param {Object} [options] - 配置选项
 * @returns {Promise<Array<{path: string, type: string}>>} - 文件列表
 */
async function fetchRepoContentsWithCache(owner, repo, options = {}) {
  const cacheKey = `github-repo-${owner}-${repo}`;
  
  try {
    // 尝试从Chrome存储中获取缓存
    const cached = await chrome.storage.local.get([cacheKey]);
    if (cached[cacheKey]) {
      const { data, timestamp } = cached[cacheKey];
      const cacheAge = Date.now() - timestamp;
      
      // 缓存有效期：5分钟
      if (cacheAge < 5 * 60 * 1000) {
        console.log('使用缓存的仓库文件列表');
        return data;
      }
    }
  } catch (error) {
    console.warn('无法访问缓存:', error);
  }

  // 获取新数据
  const fileList = await fetchRepoContents(owner, repo, '', options);
  
  try {
    // 缓存新数据
    await chrome.storage.local.set({
      [cacheKey]: {
        data: fileList,
        timestamp: Date.now()
      }
    });
  } catch (error) {
    console.warn('无法缓存数据:', error);
  }
  
  return fileList;
}

/**
 * 获取单个Markdown文件的原始内容。
 * @param {string} owner - 仓库所有者。
 * @param {string} repo - 仓库名称。
 * @param {string} filePath - 文件的路径。
 * @returns {Promise<string>} - 文件的原始文本内容。
 */
async function fetchFileContent(owner, repo, filePath) {
  const rawUrl = `https://raw.githubusercontent.com/${owner}/${repo}/main/${filePath}`;
  const response = await fetch(rawUrl);
  if (!response.ok) {
    throw new Error(`无法获取文件内容: ${response.statusText}`);
  }
  return await response.text();
}

/**
 * 合并所有Markdown文件的内容，并保持目录结构。
 * @param {string} owner - 仓库所有者。
 * @param {string} repo - 仓库名称。
 * @param {Array<{path: string, type: string}>} files - 所有Markdown文件的列表。
 * @returns {Promise<string>} - 合并后的Markdown字符串。
 */
async function combineMarkdownFiles(owner, repo, files) {
  let combinedContent = '';
  // 按照文件路径进行排序，以保持原始目录顺序
  files.sort((a, b) => a.path.localeCompare(b.path));

  for (const file of files) {
    // 为每个文件添加一个标题，反映其在仓库中的路径
    combinedContent += `\n# 文件: ${file.path}\n\n`;
    try {
      // 获取文件内容
      const content = await fetchFileContent(owner, repo, file.path);
      combinedContent += content + '\n\n---\n\n';
    } catch (error) {
      console.error(`无法获取文件 ${file.path}:`, error);
      combinedContent += `**错误: 无法加载文件内容。**\n\n---\n\n`;
    }
  }
  return combinedContent;
}

/**
 * 在新标签页中显示合并后的Markdown内容。
 * @param {string} content - 合并后的Markdown字符串。
 */
async function displayMarkdownInNewTab(content) {
  // 创建一个包含Markdown内容的新HTML页面
  const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>GitHub Markdown合并</title>
      <style>
        body { font-family: sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: auto; padding: 20px; background-color: #fff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #333; }
        textarea {
          width: 100%;
          min-height: 80vh;
          border: 1px solid #ccc;
          border-radius: 4px;
          padding: 10px;
          font-family: monospace;
          resize: vertical;
        }
        button {
          display: block;
          margin-top: 10px;
          padding: 10px 20px;
          font-size: 16px;
          cursor: pointer;
          background-color: #007bff;
          color: #fff;
          border: none;
          border-radius: 4px;
        }
        button:hover {
          background-color: #0056b3;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>GitHub Markdown 已合并</h1>
        <textarea id="markdownContent">${content}</textarea>
        <button onclick="copyContent()">复制内容</button>
      </div>
      <script>
        function copyContent() {
          const textarea = document.getElementById('markdownContent');
          textarea.select();
          document.execCommand('copy');
          alert('内容已复制到剪贴板！');
        }
      </script>
    </body>
    </html>
  `;
  
  // 使用data URL来创建新的标签页
  const blob = new Blob([htmlContent], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  await chrome.tabs.create({ url: url });
}

/**
 * 在当前页面显示一个简单的消息框。
 * @param {string} message - 要显示的消息。
 */
function displayMessage(message) {
  // 使用alert()进行快速提示。在实际项目中，更好的做法是注入一个自定义的UI元素。
  alert(message);
}
