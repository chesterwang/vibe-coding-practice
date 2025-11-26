package com.example.myapplication.data

interface SettingsRepository {
    suspend fun getSettings(): Settings
    suspend fun updateSettings(settings: Settings)
}