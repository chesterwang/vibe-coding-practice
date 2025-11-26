package com.example.myapplication.data.api

data class QwenChatRequest(
    val model: String = "qwen-turbo", // Using qwen-turbo for faster response
    val messages: List<Message>,
    val temperature: Float = 0.7f
)

data class Message(
    val role: String, // "system", "user", or "assistant"
    val content: String
)

data class QwenChatResponse(
    val id: String,
    val `object`: String,
    val created: Long,
    val model: String,
    val choices: List<Choice>,
    val usage: Usage
)

data class Choice(
    val index: Int,
    val message: Message,
    val finish_reason: String
)

data class Usage(
    val prompt_tokens: Int,
    val completion_tokens: Int,
    val total_tokens: Int
)