package com.example.myapplication.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.Settings
import com.example.myapplication.data.Todo
import com.example.myapplication.data.api.QwenApiClient
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlin.random.Random

class AiMessageViewModel : ViewModel() {
    private val _aiMessage = MutableStateFlow("")
    val aiMessage: StateFlow<String> = _aiMessage.asStateFlow()

    fun generateAiMessage(todos: List<Todo>, settings: Settings) {
        viewModelScope.launch {
            // Generate AI message based on the current todo list status
            val completedCount = todos.count { it.isCompleted }
            val totalCount = todos.size
            val pendingCount = totalCount - completedCount

            // Using Qwen API for message generation (parallel to the original function)
            val message = generateEncouragingMessageWithQwenAPI(completedCount, pendingCount, totalCount, settings.aiPrompt, todos)
            _aiMessage.value = message
        }
    }

    // New function to generate encouraging message using Qwen API
    private suspend fun generateEncouragingMessageWithQwenAPI(
        completedCount: Int,
        pendingCount: Int,
        totalCount: Int,
        aiPrompt: String,
        todos: List<Todo>
    ): String {
        // Get API key from environment or settings (in a real app, you'd want to secure this properly)
//        val apiKey = "sk-8cbd7d1f9aef4b408ade7d9c66481e03" System.getenv("QWEN_API_KEY") ?: "YOUR_QWEN_API_KEY_HERE"
        val apiKey = "sk-8cbd7d1f9aef4b408ade7d9c66481e03" ?: "YOUR_QWEN_API_KEY_HERE"

        if (apiKey == "YOUR_QWEN_API_KEY_HERE") {
            // Fallback to local generation if API key is not set
            return generateEncouragingMessage(completedCount, pendingCount, totalCount, aiPrompt, todos)
        }

        return try {
            val client = QwenApiClient(apiKey)
            val todoListText = buildString {
                append("Current TODO List Status:\n")
                append("Total tasks: $totalCount\n")
                append("Completed: $completedCount\n")
                append("Pending: $pendingCount\n\n")

                if (todos.isNotEmpty()) {
                    append("Tasks:\n")
                    todos.forEachIndexed { index, todo ->
                        val status = if (todo.isCompleted) "✓" else "○"
                        append("${index + 1}. [$status] ${todo.title}\n")
                        if (todo.description.isNotEmpty()) {
                            append("   - ${todo.description}\n")
                        }
                    }
                }
            }

            client.generateEncouragingMessage(todoListText)
        } catch (e: Exception) {
            e.printStackTrace()
            // Fallback to local generation if API call fails
            generateEncouragingMessage(completedCount, pendingCount, totalCount, aiPrompt, todos)
        }
    }

    private fun generateEncouragingMessage(
        completedCount: Int,
        pendingCount: Int,
        totalCount: Int,
        aiPrompt: String,
        todos: List<Todo>
    ): String {
        val progressPercentage = if (totalCount > 0) (completedCount * 100) / totalCount else 0

        return when {
            totalCount == 0 -> {
                "You haven't added any tasks yet! Why not start by adding something you'd like to accomplish today? Every journey begins with a single step. You've got this!"
            }
            completedCount == totalCount && totalCount > 0 -> {
                "Amazing job! You've completed all your tasks! Take a moment to celebrate your accomplishments. You're making great progress!"
            }
            progressPercentage >= 80 -> {
                "You're almost there! With $pendingCount task${if(pendingCount > 1) "s" else ""} left, you're on track to complete everything. Just a little more effort and you'll be done!"
            }
            progressPercentage >= 50 -> {
                "Great progress! You've completed $completedCount out of $totalCount tasks. You're more than halfway there. Keep up the good work!"
            }
            progressPercentage >= 25 -> {
                "You're making good progress! $completedCount out of $totalCount tasks completed. Remember, every small step counts toward your bigger goals!"
            }
            else -> {
                "You're just getting started! $completedCount task${if(completedCount > 1) "s" else ""} completed so far. Don't worry about the remaining $pendingCount - just focus on the next task and you'll build momentum!"
            }
        }
    }

    fun generateCompletionMessage(todoTitle: String): String {
        val encouragementMessages = listOf(
            "Fantastic work completing '$todoTitle'! You're making real progress toward your goals.",
            "Great job on '$todoTitle'! Each task you completes brings you closer to your objectives.",
            "Way to go on '$todoTitle'! Your dedication is really paying off.",
            "Excellent! Completing '$todoTitle' shows your commitment to productivity.",
            "Keep up the great work! '$todoTitle' is now checked off your list."
        )

        return encouragementMessages[Random.nextInt(encouragementMessages.size)]
    }
}