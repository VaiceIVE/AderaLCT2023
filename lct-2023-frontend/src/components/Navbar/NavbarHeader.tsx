import { Avatar, Flex, Stack, Title, Text, useMantineTheme } from "@mantine/core";
import { IconHome, IconLogout } from "@tabler/icons-react";
import { observer } from "mobx-react-lite";
import { useContext } from "react";
import { Context } from "../../main";

const NavbarHeader = () => {
    const { UStore } = useContext(Context);
    const theme = useMantineTheme();

    return(
        <Flex gap={16} align='center'>
            <Avatar w={56} h={56} color="red.0" radius={32}>
                <IconHome stroke="2" color={theme.colors.red[5]}/> 
            </Avatar>
            <Stack w={184} spacing={4}>
                <Title color="gray.9" size="h5">{UStore.user.username}</Title>
                <Text lh={'24px'} size="lg" color="gray.5">
                    {UStore.user.role === 'user' ? 'Аналитик' : 'Старший аналитик'}
                </Text>
            </Stack>
            <IconLogout 
                style={{marginLeft: 'auto', cursor: 'pointer'}} 
                stroke="2" 
                color={theme.colors.gray[4]}
                onClick={() => UStore.logout()}
            />
        </Flex>
    );
};

export default observer(NavbarHeader);