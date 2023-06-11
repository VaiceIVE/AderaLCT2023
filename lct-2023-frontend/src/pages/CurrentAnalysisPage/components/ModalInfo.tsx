import { Flex, Stack, Title, useMantineTheme } from "@mantine/core";
import { IconMapPin, IconX } from "@tabler/icons-react";
import { useEffect, useState } from "react";
import { IAnalysisResult } from "../../../models/IAnalysisResult";
import ModalInfoBlock from "./ModalInfoBlock";

const ModalInfo = (props: {handleModalInfoClose: Function, adress: string, result: IAnalysisResult[] | undefined}) => {
    const theme = useMantineTheme();
    const [currentResult, setCurrentResult] = useState<IAnalysisResult>();

    useEffect(() => {
        props.result?.map((item) => {
            if (item.adress === props.adress) {
                setCurrentResult(item);
            };
        })
    }, [props.result]);

    return (
        <Stack spacing={32}>
            <Flex align="center" justify="space-between">
                <Flex align="center" gap={8}>
                    <IconMapPin stroke={'2'} color={theme.colors.red[7]}/>
                    <Title size="h5" color="gray.9">{`Дом по адресу 
                        ${!props.adress.indexOf('внутригородская') ? props.adress.slice(props.adress.indexOf(',')+1).trim() :
                        props.adress
                        }`}
                    </Title>
                </Flex>
                <IconX
                    onClick={() => props.handleModalInfoClose()}
                    style={{cursor: 'pointer'}}
                    stroke={'2'}
                    color={theme.colors.gray[5]}
                />
            </Flex>
            <ModalInfoBlock stats={currentResult?.stats!} title={'Характеристика'}/>
        </Stack>
    );
};

export default ModalInfo;