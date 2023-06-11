import { Flex, Title, useMantineTheme, Text } from "@mantine/core";
import { IconStarFilled, IconStarsFilled } from "@tabler/icons-react";

const ItemHeading = (props: {type: string, date: string}) => {
    const theme = useMantineTheme();

    const title = () => {
        return (
            <Flex align="flex-start" gap={12}>
                {props.type === 'base' ? 
                    <IconStarFilled stroke={'2'} style={{color: theme.colors.red[7]}}/> :
                    <IconStarsFilled stroke={'2'} style={{color: theme.colors.red[7]}}/>
                }
                <Title size="h5" color="gray.9">
                    {props.type === 'base' ? 'Базовый анализ' : 'Продвинутый анализ'}
                </Title>
            </Flex>
        );
    };

    return (
        <Flex align="center" justify="space-between">
            {title()}
            <Text size="lg" lh={'24px'} color="gray.5">{props.date.split(".").reverse().join(".")}</Text>
        </Flex>
    );
};

export default ItemHeading;