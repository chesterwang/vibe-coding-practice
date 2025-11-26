package com.example.myapplication.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.Settings
import com.example.myapplication.data.SettingsRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class SettingsViewModel(private val repository: SettingsRepository) : ViewModel() {
    private val _settings = MutableStateFlow(Settings())
    val settings: StateFlow<Settings> = _settings.asStateFlow()

    init {
        loadSettings()
    }

    private fun loadSettings() {
        viewModelScope.launch {
            _settings.value = repository.getSettings()
        }
    }

    fun updateSettings(aiPrompt: String) {
        viewModelScope.launch {
            val updatedSettings = _settings.value.copy(aiPrompt = aiPrompt)
            repository.updateSettings(updatedSettings)
            _settings.value = updatedSettings
        }
    }
}