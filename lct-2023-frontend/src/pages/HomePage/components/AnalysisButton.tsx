import { Button } from "@mantine/core";
import { observer } from "mobx-react-lite";
import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { Context } from "../../../main";
import { CURRENT_ANALYSIS_ROUT } from "../../../utils/const";

type AnalysisButtonProps = {
    children?: React.ReactNode;
    toggle: Function;
    opened: boolean;
};

const AnalysisButton = ({children, toggle, opened}: AnalysisButtonProps) => {
    const { AStore } = useContext(Context);
    const navigate = useNavigate();

    if (children === 'Базовый анализ') {
        return (
            <Button
                fz='lg'
                w={164} h={48}
                color={AStore.currentBaseAnalysis ? 'red.7' : "gray.9"}
                fw={400}
                onClick={AStore.currentBaseAnalysis ? 
                    () => navigate(CURRENT_ANALYSIS_ROUT + '/' + 0) :
                    () => AStore.baseAnalysis()
                }
                disabled={AStore.isSmartLoading}
            >
                {AStore.currentBaseAnalysis ? 'К результату' : 'Начать'}
            </Button>
        );
    } else {
        return (
            <Button
                style={opened ? {display: 'none'} : {}}
                fz='lg'
                w={164} h={48}
                color="gray.9"
                fw={400}
                onClick={() => toggle()}
            >
                Выбрать
            </Button>
        );
    }
};

export default observer(AnalysisButton);