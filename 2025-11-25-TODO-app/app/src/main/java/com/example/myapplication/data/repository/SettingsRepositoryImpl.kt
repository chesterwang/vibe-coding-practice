package com.example.myapplication.data.repository

import com.example.myapplication.data.Settings
import com.example.myapplication.data.SettingsRepository
import com.example.myapplication.data.database.dao.SettingsDao
import com.example.myapplication.data.mapper.SettingsMapper
import com.example.myapplication.data.mapper.SettingsMapper.toSettings
import com.example.myapplication.data.mapper.SettingsMapper.toSettingsEntity
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

class SettingsRepositoryImpl(
    private val settingsDao: SettingsDao
) : SettingsRepository {
    override suspend fun getSettings(): Settings {
        return settingsDao.getSettingsSync()?.toSettings() ?: Settings()
    }

    override suspend fun updateSettings(settings: Settings) {
        val settingsEntity = settings.toSettingsEntity()
        settingsDao.insertSettings(settingsEntity)
    }
}