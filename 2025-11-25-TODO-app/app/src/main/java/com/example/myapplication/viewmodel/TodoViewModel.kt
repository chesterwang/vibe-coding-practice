package com.example.myapplication.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.Todo
import com.example.myapplication.data.TodoRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.launch

class TodoViewModel(private val repository: TodoRepository) : ViewModel() {
    private val _todos = MutableStateFlow<List<Todo>>(emptyList())
    val todos: StateFlow<List<Todo>> = _todos.asStateFlow()

    private val _completionMessage = MutableStateFlow<String?>(null)
    val completionMessage: StateFlow<String?> = _completionMessage.asStateFlow()

    init {
        // Observe the flow from the repository
        repository.getAllTodosFlow()
            .onEach { _todos.value = it }
            .launchIn(viewModelScope)
    }

    fun addTodo(title: String, description: String = "") {
        viewModelScope.launch {
            val newTodo = Todo(title = title, description = description)
            repository.insertTodo(newTodo)
        }
    }

    fun updateTodo(todo: Todo) {
        viewModelScope.launch {
            repository.updateTodo(todo)
        }
    }

    fun deleteTodo(id: String) {
        viewModelScope.launch {
            repository.deleteTodo(id)
        }
    }

    fun toggleTodoCompletion(id: String) {
        viewModelScope.launch {
            val todo = repository.getTodoById(id)
            if (todo != null) {
                val isCompleted = !todo.isCompleted
                repository.updateTodoCompletion(id, isCompleted)

                // If the todo was just completed, generate an encouragement message
                if (isCompleted) {
                    _completionMessage.value = generateEncouragementMessage(todo.title)
                }
            }
        }
    }

    fun clearCompletedTodos() {
        viewModelScope.launch {
            val completedTodos = _todos.value.filter { it.isCompleted }
            completedTodos.forEach { todo ->
                repository.deleteTodo(todo.id)
            }
        }
    }

    fun clearCompletionMessage() {
        _completionMessage.value = null
    }

    private fun generateEncouragementMessage(todoTitle: String): String {
        // In a real app, this would connect to the AI message ViewModel
        // For now, we'll return a formatted message that the UI can display
        return "Great job completing '$todoTitle'! This is an important step towards your goals."
    }
}

data class TodoUiState(
    val title: String = "",
    val description: String = ""
)