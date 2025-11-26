package com.example.myapplication

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.input.nestedscroll.nestedScroll
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.example.myapplication.data.database.AppDatabase
import com.example.myapplication.data.repository.SettingsRepositoryImpl
import com.example.myapplication.data.repository.TodoRepositoryImpl
import com.example.myapplication.ui.components.SettingsScreen
import com.example.myapplication.ui.theme.MyApplicationTheme
import com.example.myapplication.viewmodel.SettingsViewModel

import com.example.myapplication.MainScreen

class MainActivity : ComponentActivity() {
    @OptIn(ExperimentalMaterial3Api::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val database = AppDatabase.getDatabase(this)
        val todoRepository = TodoRepositoryImpl(database.todoDao())
        val settingsRepository = SettingsRepositoryImpl(database.settingsDao())

        enableEdgeToEdge()
        setContent {
            MyApplicationTheme {
                AppNavigation(
                    todoRepository = todoRepository,
                    settingsRepository = settingsRepository
                )
            }
        }
    }
}



@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AppNavigation(
    todoRepository: TodoRepositoryImpl,
    settingsRepository: SettingsRepositoryImpl
) {
    val navController = rememberNavController()
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentScreen = AppScreen.fromRoute(backStackEntry?.destination?.route)

    val scrollBehavior = TopAppBarDefaults.exitUntilCollapsedScrollBehavior()

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            if (currentScreen == AppScreen.Main) {
                TopAppBar(
                    title = { Text("AI-Powered TODO List") },
                    actions = {
                        IconButton(onClick = { navController.navigate(AppScreen.Settings.route) }) {
                            Icon(
                                imageVector = Icons.Default.Settings,
                                contentDescription = "Settings"
                            )
                        }
                    },
                    scrollBehavior = scrollBehavior
                )
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = AppScreen.Main.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(AppScreen.Main.route) {
                MainScreen(
                    todoRepository = todoRepository,
                    settingsRepository = settingsRepository,
                    navigateToSettings = { navController.navigate(AppScreen.Settings.route) }
                )
            }
            composable(AppScreen.Settings.route) {
                SettingsScreenContent(
                    settingsRepository = settingsRepository,
                    onBack = { navController.popBackStack() }
                )
            }
        }
    }
}

@Composable
fun SettingsScreenContent(
    settingsRepository: SettingsRepositoryImpl,
    onBack: () -> Unit
) {
    val settingsViewModel: SettingsViewModel = viewModel { SettingsViewModel(settingsRepository) }
    val settings by settingsViewModel.settings.collectAsState()

    com.example.myapplication.ui.components.SettingsScreen(
        settings = settings,
        onSettingsUpdate = { aiPrompt -> settingsViewModel.updateSettings(aiPrompt) },
        onBack = onBack
    )
}