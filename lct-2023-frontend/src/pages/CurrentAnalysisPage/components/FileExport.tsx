import { Autocomplete, Button, createStyles, Flex, Stack, TextInput, ThemeIcon, Title, Text, Transition, Paper } from "@mantine/core";
import { IconQuestionMark } from "@tabler/icons-react";
import { useState } from "react";
import AnalysisServices from "../../../services/AnalysisServices";

const useStyles = createStyles((theme) => ({
    wrapper: {
        padding: '24px',
        borderRadius: '16px',
        background: theme.colors.gray[0],
        width: '369px',
        position: 'relative'
    },
    info: {
        padding: '8px 16px',
    }
}));

const FileExport = (props: {id: string}) => {
    const { classes } = useStyles();
    const [type, setType] = useState<string>('');
    const [fileName, setFileName] = useState<string>('');
    const [hover, setHover] = useState<boolean>(false);

    const handleDownload = async () => {
        const response = await AnalysisServices.fileExport(fileName, type, props.id);
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${fileName}${type}`);
        document.body.appendChild(link);
        link.click();
    };

    return (
        <Flex className={classes.wrapper}>
            <Stack spacing={24}>
                <Flex align="center" justify="space-between">
                    <Transition mounted={hover} transition="fade" duration={200} timingFunction="ease">
                        {(styles) => (
                        <Paper
                            shadow="md"
                            style={{ ...styles, 
                                position: 'absolute', 
                                top: 60, left: 70, 
                                right: 0,
                                padding: '8px 16px'
                            }}
                        >
                            <Text size="lg" lh={'24px'} color="gray.9">
                                Перед экспортом сохраните файл
                            </Text>
                        </Paper>
                        )}
                    </Transition>
                    <Title size="h4" color="gray.9">Параметры экспорта</Title>
                    <ThemeIcon 
                        style={{cursor: 'pointer'}} 
                        radius="xl" 
                        color="gray.4"
                        onMouseEnter={() => setHover(true)}
                        onMouseLeave={() => setHover(false)}
                    >
                        <IconQuestionMark width={20} height={20} stroke="2" color='#343A40'/>
                    </ThemeIcon>
                </Flex>
                <Stack spacing={16}>
                    <Autocomplete
                        data={['.xlsx', '.xls', '.csv']}
                        placeholder='.xlsx'
                        label="Тип файла"
                        className="input"
                        size="lg"
                        w={321}
                        value={type}
                        onChange={setType}
                    />
                    <TextInput
                        label="Имя файла"
                        className="input"
                        size="lg"
                        w={321}
                        placeholder="Сводка по работам"
                        onChange={(e) => setFileName(e.currentTarget.value)}
                        value={fileName}
                    />
                </Stack>
                <Button
                    fz='lg'
                    w={321} h={48}
                    color="gray.9"
                    fw={400}
                    disabled={!type || !fileName}
                    onClick={handleDownload}
                >
                    Скачать файл
                </Button>
            </Stack>
        </Flex>
    );
};

export default FileExport;