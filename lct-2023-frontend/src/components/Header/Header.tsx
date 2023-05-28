import { Button, Flex, Title } from "@mantine/core";
import { useContext, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { CURRENT_ANALYSIS_ROUT, MAPS_ROUTE } from "../../utils/const";
import { authRoutes } from "../../utils/routes";
import { IconArrowLeft } from '@tabler/icons-react';
import { Context } from "../../main";
import { observer } from "mobx-react-lite";
import AnalysisServices from "../../services/AnalysisServices";
import _cloneDeep from 'lodash'
import _ from "lodash";

const Header = () => {
    const { AStore } = useContext(Context);
    const location = useLocation();
    const navigate = useNavigate();
    const [title, setTitle] = useState<string>('');

    useEffect(() => {
        if (!location.pathname.indexOf('/analysis')) {
            setTitle('Результаты анализа');
        } else {
            const titleIdAuth = authRoutes.map(e => e.path).indexOf(location.pathname);
            setTitle(authRoutes[titleIdAuth].title);
        }
    }, [location]);

    const handleUpdate = () => {
        console.log(_.cloneDeep(AStore.analysis!));
        try {
            AnalysisServices.saveAnalysis(_.cloneDeep(AStore.analysis!)) 
        } catch (error) {
            console.log(error)
        }
    };

    return (
        <Flex align="center" gap={16} style={{padding: '48px 24px 24px', width: '100%'}}>
            {(!location.pathname.indexOf(CURRENT_ANALYSIS_ROUT) || location.pathname === MAPS_ROUTE) ? 
                <IconArrowLeft style={{cursor: 'pointer'}} onClick={() => navigate(-1)} stroke={'2'}/>
            : <></>}
            <Title size="h2" color="gray.9">{title}</Title>
            {!location.pathname.indexOf(CURRENT_ANALYSIS_ROUT) ?
                <Button
                    fz='lg'
                    w={198} h={48}
                    color={'red.7'}
                    fw={400}
                    style={{marginLeft: 'auto'}}
                    onClick={handleUpdate}
                >
                    Сохранить
                </Button>
            : <></>}
        </Flex>
    );
};

export default observer(Header);