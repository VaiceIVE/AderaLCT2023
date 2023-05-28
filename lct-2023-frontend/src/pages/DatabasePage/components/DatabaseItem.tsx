import { Flex, useMantineTheme, Text, ActionIcon } from "@mantine/core";
import { IconDownload, IconFile } from "@tabler/icons-react";
import DatabaseServices from "../../../services/DatabaseServices";

const DatabaseItem = (props: {file: string}) => {
    const theme = useMantineTheme();

    const handleClick = async () => {
        const response = await DatabaseServices.databaseExport(props.file);
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${props.file}.xlsx`);
        document.body.appendChild(link);
        link.click();
    };

    return (
        <Flex style={{padding: '16px', borderRadius: '8px', background: '#F8F9FA'}} w={700} gap={8}>
            <IconFile color={theme.colors.gray[5]} stroke={2}/>
            <Text lh={'24px'} size="lg" color="gray.9">{props.file}</Text>
            <ActionIcon onClick={handleClick} style={{marginLeft: 'auto'}}>
                <IconDownload  color={theme.colors.gray[5]} stroke={2}/>
            </ActionIcon>
        </Flex>
    );
};

export default DatabaseItem;