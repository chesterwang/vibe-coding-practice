package com.example.myapplication.data.database.dao

import androidx.room.*
import com.example.myapplication.data.database.entities.TodoEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface TodoDao {
    @Query("SELECT * FROM todos ORDER BY created_at DESC")
    fun getAllTodos(): Flow<List<TodoEntity>>

    @Query("SELECT * FROM todos WHERE id = :id")
    suspend fun getTodoById(id: String): TodoEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTodo(todo: TodoEntity)

    @Update
    suspend fun updateTodo(todo: TodoEntity)

    @Delete
    suspend fun deleteTodo(todo: TodoEntity)

    @Query("DELETE FROM todos WHERE id = :id")
    suspend fun deleteTodoById(id: String)

    @Query("DELETE FROM todos")
    suspend fun deleteAllTodos()

    @Query("UPDATE todos SET isCompleted = :isCompleted, completed_at = :completedAt WHERE id = :id")
    suspend fun updateTodoCompletion(id: String, isCompleted: Boolean, completedAt: java.time.LocalDateTime?)
}