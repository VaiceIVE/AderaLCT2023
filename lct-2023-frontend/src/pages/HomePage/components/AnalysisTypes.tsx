import { Stack } from "@mantine/core";
import AnalysisWrapper from "../../../components/Wrappers/AnalysisWrapper";
import BlockWrapper from "../../../components/Wrappers/BlockWrapper";

const AnalysisTypes = () => {

    return (
        <BlockWrapper>
            Виды анлиза
            <Stack spacing={8}>
                <AnalysisWrapper>
                    Базовый анализ
                </AnalysisWrapper>
                
                <AnalysisWrapper>
                    Продвинутый анализ
                </AnalysisWrapper>
                
            </Stack>
        </BlockWrapper>
    );
};

export default AnalysisTypes;