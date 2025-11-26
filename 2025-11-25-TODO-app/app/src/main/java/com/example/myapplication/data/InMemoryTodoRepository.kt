package com.example.myapplication.data

import android.os.Build
import androidx.annotation.RequiresApi
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class InMemoryTodoRepository : TodoRepository {
    private val _todos = MutableStateFlow<List<Todo>>(emptyList())
    val todos: StateFlow<List<Todo>> = _todos.asStateFlow()
    
    private val mutex = Mutex()
    override fun getAllTodosFlow(): Flow<List<Todo>> {
        TODO("Not yet implemented")
    }

    override suspend fun getAllTodos(): List<Todo> {
        mutex.withLock {
            return _todos.value
        }
    }

    override suspend fun getTodoById(id: String): Todo? {
        mutex.withLock {
            return _todos.value.find { it.id == id }
        }
    }

    override suspend fun insertTodo(todo: Todo) {
        mutex.withLock {
            val current = _todos.value.toMutableList()
            current.add(todo)
            _todos.value = current
        }
    }

    override suspend fun updateTodo(todo: Todo) {
        mutex.withLock {
            val current = _todos.value.toMutableList()
            val index = current.indexOfFirst { it.id == todo.id }
            if (index != -1) {
                current[index] = todo
                _todos.value = current
            }
        }
    }

    override suspend fun deleteTodo(id: String) {
        mutex.withLock {
            val current = _todos.value.toMutableList()
            current.removeAll { it.id == id }
            _todos.value = current
        }
    }

    override suspend fun deleteAllTodos() {
        mutex.withLock {
            _todos.value = emptyList()
        }
    }

    @RequiresApi(Build.VERSION_CODES.O)
    override suspend fun updateTodoCompletion(id: String, isCompleted: Boolean) {
        mutex.withLock {
            val current = _todos.value.toMutableList()
            val index = current.indexOfFirst { it.id == id }
            if (index != -1) {
                val todo = current[index]
                current[index] = todo.copy(
                    isCompleted = isCompleted,
                    completedAt = if (isCompleted) java.time.LocalDateTime.now() else null
                )
                _todos.value = current
            }
        }
    }
}