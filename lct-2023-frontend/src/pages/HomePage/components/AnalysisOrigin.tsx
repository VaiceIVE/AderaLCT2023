import { createStyles, Flex, Group, Radio, SegmentedControl, Stack, TextInput } from "@mantine/core";
import FileUpload from "./FileUpload";

const useStyles = createStyles((_theme) => ({
    segment: {
        input: {
            background: '#F8F9FA'
        },
        label: {
            fontSize: '16px',
            lineHeight: '24px',
            padding: '4px 12px'
        },
    },
    radio: {
        div: {
            fontSize: '16px',
            lineHeight: '24px'
        }
    }

}));

interface AnalysisOriginProps {
    origin: string;
    setOrigin: React.Dispatch<React.SetStateAction<string>>;
    url: string;
    setUrl: React.Dispatch<React.SetStateAction<string>>;
}

const AnalysisOrigin = ({ origin, setOrigin, url, setUrl }: AnalysisOriginProps) => {
    const { classes } = useStyles();
    
    return (
        <Stack spacing={24}>
            <SegmentedControl
                value={origin}
                onChange={setOrigin}
                className={classes.segment}
                data={[
                    { label: 'База данных', value: 'database' },
                    { label: 'Сторонний сервис', value: 'url', disabled: true },
                    { label: 'Загрузка', value: 'download', disabled: true },
                ]}
                w={380}
                lh={'24px'}
            />
            {origin === 'url' ?
                <Flex align="flex-start" gap={24}>
                    <TextInput
                        className='input'
                        w={443.5}
                        value={url}
                        onChange={(e) => setUrl(e.currentTarget.value)} 
                        lh={'24px'}
                        size="lg"
                        label="Выберите источник"
                        placeholder="http://localhost:3000/"
                    />
                    <Radio.Group
                        name="favoriteFramework"
                        label="Укажите тип файла"
                        className={classes.radio}
                    >
                        <Group mt="xs">
                            <Radio color="red.7" 
                                size="md" value="react" label="React" 
                            />
                            <Radio color="red.7" 
                                size="md" value="svelte" label="Svelte" 
                            />
                            <Radio color="red.7" 
                                size="md" value="ng" label="Angular" 
                            />
                        </Group>
                    </Radio.Group>
                </Flex>
            : origin === 'download' ? 
                <FileUpload/>
            : <></>}
        </Stack>
    );
};

export default AnalysisOrigin;