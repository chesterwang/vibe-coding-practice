package com.example.myapplication.data.api

import android.util.Log
import com.openai.client.OpenAIClient;
import com.google.gson.Gson
import com.openai.client.okhttp.OpenAIOkHttpClient
import com.openai.models.chat.completions.ChatCompletion
import com.openai.models.chat.completions.ChatCompletionCreateParams
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.IOException

class QwenApiClient(
    private val apiKey: String,
    private val baseUrl: String = "https://dashscope.aliyuncs.com/api/v1"
) {
    private val client: OpenAIClient = OpenAIOkHttpClient.builder()
        .apiKey("sk-8cbd7d1f9aef4b408ade7d9c66481e03")
        .baseUrl("https://dashscope.aliyuncs.com/compatible-mode/v1")
        .build();

//        OkHttpClient.Builder()
//        .connectTimeout(30, TimeUnit.SECONDS)
//        .readTimeout(60, TimeUnit.SECONDS)
//        .writeTimeout(60, TimeUnit.SECONDS)
//        .build()

    private val gson = Gson()

    suspend fun generateEncouragingMessage(todoListText: String): String =
        withContext(Dispatchers.IO) {
            val prompt = """
            Based on the following to-do list and symbol status, generate an encouraging and motivational message:
            
            $todoListText
            
            The message should be positive and supportive, acknowledging the user's progress and efforts.
            使用中文回答。
        """.trimIndent()

            val requestBody = QwenChatRequest(
                messages = listOf(
                    Message(
                        role = "system",
                        content = "You are a helpful assistant that provides encouraging and motivational messages related to task management and productivity."
                    ),
                    Message(
                        role = "user",
                        content = prompt
                    )
                )
            )

            val systemMessage =
                "你是曾国藩，可以 provides encouraging and motivational messages related to task management and productivity."

            val params: ChatCompletionCreateParams = ChatCompletionCreateParams.builder()
                .addSystemMessage(systemMessage)
                .addUserMessage(prompt)
                .model("qwen-turbo")
                .build();

                Log.e("prompt",prompt)

            try {
                val chatCompletion: ChatCompletion = client.chat().completions().create(params);
                System.out.println(chatCompletion);
                Log.e("test","asdfasdfsdafds")
                val result = chatCompletion.choices()[0].message().content().get()
//                client.close();
//                Log.e("client","close")
                "AI生成提醒（曾国藩话语）： " +result
            } catch (e: Exception) {
                System.err.println("Error occurred: " + e.message);
                e.printStackTrace();
//                client.close();
                throw IOException("Error calling Qwen API: ${e.message}")
            }

        }
}