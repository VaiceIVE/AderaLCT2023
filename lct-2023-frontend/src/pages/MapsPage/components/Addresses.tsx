import { Flex, List, Text, createStyles } from "@mantine/core";
import { observer } from "mobx-react-lite";
import { useContext } from "react";
import BlockWrapper from "../../../components/Wrappers/BlockWrapper";
import { Context } from "../../../main";

const useStyles = createStyles((theme) => ({

    wrapper: {
        padding: '24px',
        background: theme.colors.gray[0],
        borderRadius: '16px',
        width: '369px'
    }
}))

const Addresses = () => {
    const { MStore } = useContext(Context);
    const { classes } = useStyles();

    return (
        <Flex className={classes.wrapper}>
            <BlockWrapper>
                Выбранные адреса
                <List spacing={16}>
                    {MStore.addresses.map((item: string, index) => (
                        <List.Item key={index}>
                            <Text color="gray.9" size="lg" lh={'24px'} >
                                {item}
                            </Text>
                        </List.Item>
                    ))}
                </List>
            </BlockWrapper>
        </Flex>
    );
};

export default observer(Addresses);