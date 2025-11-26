package com.example.myapplication.data.mapper

import com.example.myapplication.data.Todo
import com.example.myapplication.data.database.entities.TodoEntity
import com.example.myapplication.data.Settings
import com.example.myapplication.data.database.entities.SettingsEntity

object TodoMapper {
    fun TodoEntity.toTodo(): Todo {
        return Todo(
            id = this.id,
            title = this.title,
            description = this.description,
            isCompleted = this.isCompleted,
            createdAt = this.createdAt,
            completedAt = this.completedAt
        )
    }

    fun Todo.toTodoEntity(): TodoEntity {
        return TodoEntity(
            id = this.id,
            title = this.title,
            description = this.description,
            isCompleted = this.isCompleted,
            createdAt = this.createdAt,
            completedAt = this.completedAt
        )
    }
}

object SettingsMapper {
    fun SettingsEntity?.toSettings(): Settings {
        return Settings(
            aiPrompt = this?.aiPrompt ?: "You are an encouraging assistant that motivates users to complete their tasks. The user has a list of tasks, some completed and some not. Generate an encouraging message that motivates them to continue working on their tasks. Be positive and supportive."
        )
    }

    fun Settings.toSettingsEntity(): SettingsEntity {
        return SettingsEntity(
            aiPrompt = this.aiPrompt
        )
    }
}