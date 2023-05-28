import { Flex, Text } from "@mantine/core";
import { IconQuestionMark } from '@tabler/icons-react';
import { useNavigate } from "react-router-dom";
import { HELP_ROUTE } from "../../utils/const";

const NavbarHelp = () => {
    const navigate = useNavigate();

    return (
        <Flex onClick={() => navigate(HELP_ROUTE)} gap={24} align="center" style={{padding: '12px 16px', cursor: 'pointer'}}>
            <IconQuestionMark stroke="2" color='#343A40'/>
            <Text color="gray.8" size="lg" lh={'24px'}>Помощь</Text>
        </Flex>
    );
};

export default NavbarHelp;