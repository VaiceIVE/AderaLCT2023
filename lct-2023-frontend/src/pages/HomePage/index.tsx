import { Stack } from "@mantine/core";
import { FC } from "react";
import Wrapper from "../../components/Wrappers/Wrapper";
import AnalysisTypes from "./components/AnalysisTypes";

const HomePage: FC = () => {
    
    return (
        
        <Wrapper>
            <Stack>
                <AnalysisTypes/>
            </Stack>
            <></>
        </Wrapper>
    );
}

export default HomePage;