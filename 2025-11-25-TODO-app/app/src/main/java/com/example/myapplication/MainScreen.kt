package com.example.myapplication

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.myapplication.data.repository.SettingsRepositoryImpl
import com.example.myapplication.data.repository.TodoRepositoryImpl
import com.example.myapplication.ui.components.AiMessageView
import com.example.myapplication.ui.components.TodoListView
import com.example.myapplication.viewmodel.AiMessageViewModel
import com.example.myapplication.viewmodel.SettingsViewModel
import com.example.myapplication.viewmodel.TodoViewModel


@Composable
fun MainScreen(
    todoRepository: TodoRepositoryImpl,
    settingsRepository: SettingsRepositoryImpl,
    navigateToSettings: () -> Unit
) {
    val todoViewModel: TodoViewModel = viewModel { TodoViewModel(todoRepository) }
    val settingsViewModel: SettingsViewModel = viewModel { SettingsViewModel(settingsRepository) }
    val aiMessageViewModel: AiMessageViewModel = viewModel { AiMessageViewModel() }

    val todos by todoViewModel.todos.collectAsState()
    val settings by settingsViewModel.settings.collectAsState()
    val aiMessage by aiMessageViewModel.aiMessage.collectAsState()
    val completionMessage by todoViewModel.completionMessage.collectAsState()

    // Update AI message when todos change
    androidx.compose.runtime.LaunchedEffect(todos) {
        aiMessageViewModel.generateAiMessage(todos, settings)
    }

    Column(modifier = Modifier.fillMaxSize()) {
        // Top half: Todo List
        TodoListView(
            todos = todos,
            onToggleComplete = { id ->
                todoViewModel.toggleTodoCompletion(id)
                // Regenerate AI message after completion
                aiMessageViewModel.generateAiMessage(todos, settings)
            },
            onDeleteTodo = { id -> todoViewModel.deleteTodo(id) },
            onAddTodo = { title, description -> todoViewModel.addTodo(title, description) },
            modifier = Modifier
                .weight(0.7f)
                .fillMaxWidth()
        )

        // Bottom half: AI Messages
        AiMessageView(
//            message = if (completionMessage != null) completionMessage!! else aiMessage,
            message = aiMessage,
            modifier = Modifier
                .weight(0.3f)
                .fillMaxWidth()
        )
    }
}