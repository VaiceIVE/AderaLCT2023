import AuthPage from "../pages/AuthPage"
import DatabasePage from "../pages/DatabasePage"
import HistoryPage from "../pages/HistoryPage"
import HomePage from "../pages/HomePage"
import { CURRENT_ANALYSIS_ROUT, DATABASE_ROUTE, HELP_ROUTE, HISTORY_ROUTE, HOME_ROUTE, LOGIN_ROUTE, MAPS_ROUTE, REGISTRATION_ROUTE } from "./const"
import { IconList, IconHistory, IconDeviceAnalytics } from '@tabler/icons-react';
import CurrentAnalysisPage from "../pages/CurrentAnalysisPage"
import HelpPage from "../pages/HelpPage"
import MapsPage from "../pages/MapsPage"

export const authRoutes = [
    {
        path: HOME_ROUTE,
        Component: HomePage,
        title: 'Анализатор',
        icon: IconDeviceAnalytics
    },
    {
        path: HISTORY_ROUTE,
        Component: HistoryPage,
        title: 'История анализов',
        icon: IconHistory
    },
    {
        path: DATABASE_ROUTE,
        Component: DatabasePage,
        title: 'База данных',
        icon: IconList
    },
    {
        path: CURRENT_ANALYSIS_ROUT + '/:id',
        Component: CurrentAnalysisPage,
        title: 'Результаты анализа',
        icon: IconList
    },
    {
        path: HELP_ROUTE,
        Component: HelpPage,
        title: 'Подсказки',
        icon: IconList
    },
    {
        path: MAPS_ROUTE,
        Component: MapsPage,
        title: 'Результаты на карте',
        icon: IconList
    }
]

export const publicRoutes = [
    {
        path: LOGIN_ROUTE,
        Component: AuthPage,
        title: 'login',
    },
    {
        path: REGISTRATION_ROUTE,
        Component: AuthPage,
        title: 'registration',
    },
]