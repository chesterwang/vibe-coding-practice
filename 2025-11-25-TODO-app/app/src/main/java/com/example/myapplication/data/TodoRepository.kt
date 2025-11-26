package com.example.myapplication.data

import kotlinx.coroutines.flow.Flow

interface TodoRepository {
    fun getAllTodosFlow(): Flow<List<Todo>>
    suspend fun getAllTodos(): List<Todo>
    suspend fun getTodoById(id: String): Todo?
    suspend fun insertTodo(todo: Todo)
    suspend fun updateTodo(todo: Todo)
    suspend fun deleteTodo(id: String)
    suspend fun deleteAllTodos()
    suspend fun updateTodoCompletion(id: String, isCompleted: Boolean)
}