import { Flex, Stack } from "@mantine/core";
import { observer } from "mobx-react-lite";
import { useContext, useEffect, useState } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Context } from "../main";
import { CURRENT_ANALYSIS_ROUT, MAPS_ROUTE } from "../utils/const";
import { authRoutes, publicRoutes } from "../utils/routes";
import Header from "./Header/Header";
import NavbarNested from "./Navbar/Navbar";

const AppRouter = () => {
    const { UStore, AStore } = useContext(Context);
    const location = useLocation();
    const [currentRoute, setCurrentRoute] = useState<boolean>(false);

    useEffect(() => {
        if (!location.pathname.indexOf(CURRENT_ANALYSIS_ROUT)) {
            setCurrentRoute(true);
        };
        if (currentRoute && (location.pathname != MAPS_ROUTE && location.pathname != '/analysis/0')) {
            setCurrentRoute(false);
            AStore.setCurrentBaseAnalysis(undefined);
            AStore.setCurrentSmartAnalysis(undefined);
        };
    }, [location]);

    if ((!AStore.currentBaseAnalysis && !AStore.currentSmartAnalysis) && location.pathname === '/analysis/0') {
        return <Navigate to='/' replace/>
    };

    if (UStore.isAuth && (location.pathname === '/login' || location.pathname === '/registration')) {
        return <Navigate to='/' replace/>
    };

    if (!UStore.isAuth && 
        (location.pathname === '/' || location.pathname === '/history' || location.pathname === '/database' ||
        location.pathname === '/help' || location.pathname === '/maps')) {
        return <Navigate to='/login' replace/>
    };

    return (
        <Flex>
            {(UStore.isAuth && (location.pathname !== '/login' && location.pathname !== '/registration')) ? <NavbarNested/> : <></>}
            <Stack spacing="0rem">
                {(UStore.isAuth && (location.pathname !== '/login' && location.pathname !== '/registration')) ? <Header/> : <></>}
                <Routes>
                    {UStore.isAuth && authRoutes.map(({path, Component}) => 
                        <Route key={path} path={path} element={<Component/>}/>
                    )}
                    {publicRoutes.map(({path, Component}) => 
                        <Route key={path} path={path} element={<Component/>}/>
                    )}
                </Routes>
            </Stack>
        </Flex>
    );
};

export default observer(AppRouter);