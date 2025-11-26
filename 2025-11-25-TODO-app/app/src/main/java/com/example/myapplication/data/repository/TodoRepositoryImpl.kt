package com.example.myapplication.data.repository

import android.os.Build
import androidx.annotation.RequiresApi
import com.example.myapplication.data.Todo
import com.example.myapplication.data.TodoRepository
import com.example.myapplication.data.database.dao.TodoDao
import com.example.myapplication.data.database.entities.TodoEntity
import com.example.myapplication.data.mapper.TodoMapper
import com.example.myapplication.data.mapper.TodoMapper.toTodo
import com.example.myapplication.data.mapper.TodoMapper.toTodoEntity
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

class TodoRepositoryImpl(
    private val todoDao: TodoDao
) : TodoRepository {
    override fun getAllTodosFlow(): Flow<List<Todo>> {
        return todoDao.getAllTodos().map { entities -> entities.map { entity -> entity.toTodo() } }
    }

    override suspend fun getAllTodos(): List<Todo> {
        return todoDao.getAllTodos().map { entities -> entities.map { entity -> entity.toTodo() } }.first()
    }

    override suspend fun getTodoById(id: String): Todo? {
        return todoDao.getTodoById(id)?.toTodo()
    }

    override suspend fun insertTodo(todo: Todo) {
        todoDao.insertTodo(todo.toTodoEntity())
    }

    override suspend fun updateTodo(todo: Todo) {
        todoDao.updateTodo(todo.toTodoEntity())
    }

    override suspend fun deleteTodo(id: String) {
        todoDao.deleteTodoById(id)
    }

    override suspend fun deleteAllTodos() {
        todoDao.deleteAllTodos()
    }

    @RequiresApi(Build.VERSION_CODES.O)
    override suspend fun updateTodoCompletion(id: String, isCompleted: Boolean) {
        todoDao.updateTodoCompletion(
            id = id,
            isCompleted = isCompleted,
            completedAt = if (isCompleted) java.time.LocalDateTime.now() else null
        )
    }
}