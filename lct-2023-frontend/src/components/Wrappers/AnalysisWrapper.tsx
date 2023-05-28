import { Collapse, createStyles, Flex, LoadingOverlay, Stack, Text, Title, useMantineTheme } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { IconStarFilled, IconStarsFilled, IconX } from '@tabler/icons-react';
import { observer } from "mobx-react-lite";
import { useContext, useEffect, useState } from "react";
import { Context } from "../../main";
import AnalysisButton from "../../pages/HomePage/components/AnalysisButton";
import AnalysisForm from "../../pages/HomePage/components/AnalysisForm";

const useStyles = createStyles((theme, opened: boolean) => ({
    wrapper: {
        padding: opened ? '25px' : '24px',
        border: opened ? '' : '1px solid #E9ECEF',
        borderRadius: '16px',
        background: opened ? theme.colors.gray[0] : ''
    },
}));

type Props = {
    children?: React.ReactNode;
};

const AnalysisWrapper = ({children}: Props) => {
    const theme = useMantineTheme();
    const [opened, { toggle }] = useDisclosure(false);
    const { classes } = useStyles(opened);
    const [tarnsition, setTransition] = useState<Boolean>(false);
    const [baseLoading, setBaseLoading] = useState<boolean>(false);
    const [smartLoading, setSmartLoading] = useState<boolean>(false);
    const { AStore } = useContext(Context);

    useEffect(() => {
        setBaseLoading(AStore.isBaseLoading);
        setSmartLoading(AStore.isSmartLoading);
    }, [AStore.isBaseLoading || AStore.isSmartLoading])

    const title = () => {
        return (
            <Flex justify="space-between">
                <Flex align="flex-start" gap={12}>
                    {children ? children === 'Базовый анализ' ? 
                        <IconStarFilled stroke={'2'} style={{color: theme.colors.red[7]}}/> :
                        <IconStarsFilled stroke={'2'} style={{color: theme.colors.red[7]}}/>
                    : <></>}
                    <Stack spacing={4}>
                        <Title color="gray.9" size="h5">{children ? children : <></>}</Title>
                        {children ? children === 'Базовый анализ' ? 
                        <Text color="gray.5" lh={'20px'} size="md">~ 30 сек</Text> :
                        <Text color="gray.5" lh={'20px'} size="md">~ 1 мин</Text>
                        : <></>}
                    </Stack>
                </Flex>
                <IconX 
                    onClick={toggle} 
                    stroke={'2'} 
                    color={theme.colors.gray[5]} 
                    style={!opened ? {display: 'none'} : {cursor: 'pointer'}}
                />
            </Flex>
        );
    };

    return (
        <Flex pos="relative" align={opened ? "flex-start" : "flex-end"} justify="space-between" className={classes.wrapper}>
            <LoadingOverlay 
                visible={(baseLoading && children==='Базовый анализ') || (smartLoading && children==='Продвинутый анализ')} 
                overlayBlur={2} loaderProps={{color: 'red.5'}}/>
            <Flex direction="column">
                <Stack spacing={8}>
                    {title()}
                    <Text size="lg" color="gray.6" lh={'24px'}>
                        Анализ с системным учетом параметров, по данным 
                        полученным из базы даных
                    </Text>
                </Stack>
                {children === 'Базовый анализ' ? <></> :
                    <Collapse 
                        onTransitionEnd={() => setTransition(!tarnsition)} 
                        in={opened}
                    >
                        <AnalysisForm/>
                    </Collapse>
                }
            </Flex>
            
            {!tarnsition &&
                <AnalysisButton opened={opened} toggle={toggle}>
                    {children ? children : <></>}
                </AnalysisButton>
            }
        </Flex>
    );
};

export default observer(AnalysisWrapper);