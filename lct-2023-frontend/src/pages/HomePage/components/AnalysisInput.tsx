import { Autocomplete, createStyles, Flex, Stack } from "@mantine/core";
import { DatePickerInput } from "@mantine/dates";
import { useEffect, useState } from "react";
import AnalysisServices from "../../../services/AnalysisServices";

const useStyles = createStyles((_theme) => ({
    job: {
        input: {
            background: '#F8F9FA'
        },
        label: {
            marginBottom: '4px',
        }
    },
    wrapper: {
        marginTop: '24px'
    },
}));

interface AnalysisInputProps {
    work: string;
    object: string;
    date: [Date | null, Date | null];
    setWork?: React.Dispatch<React.SetStateAction<string>> | undefined;
    setObject?: React.Dispatch<React.SetStateAction<string>> | undefined;
    setDate?: React.Dispatch<React.SetStateAction<[Date | null, Date | null]>> | undefined;
    disabled?: boolean;
}

const AnalysisInput = ({ work, object, date, setWork, setObject, setDate, disabled }: AnalysisInputProps) => {
    const { classes } = useStyles();
    const [worktype, setWorktype] = useState<string[]>();
    const [objcategories, setObjcategories] = useState<string[]>();

    useEffect(() => {
        try {
            AnalysisServices.setObjcategories().then(response => {
                setObjcategories(response.data);
            });
            AnalysisServices.setWorktypes().then(response => {
                setWorktype(response.data);
            });
        } catch (e) {
            console.log(e)
        }
    }, []);

    return (
        <Stack spacing={disabled ? 16 : 24}>
            <Flex className={disabled ? '' : classes.wrapper} gap={16}>
                {objcategories &&
                <Autocomplete
                    className='input'
                    w={443.5}
                    lh={'24px'}
                    size="lg"
                    value={object}
                    onChange={setObject ? setObject : () => {}}
                    label="Категория объекта"
                    limit={6}
                    data={objcategories!}
                    placeholder="Двор"
                    disabled={disabled}
                />}
                <DatePickerInput
                    valueFormat="YYYY-MM-DD"
                    className='input'
                    w={443.5}
                    size="lg"
                    lh={'24px'}
                    type="range"
                    label="Отчетный период"
                    value={date}
                    onChange={setDate ? setDate : () => {}}
                    disabled={disabled}
                />
            </Flex>
            {worktype &&
            <Autocomplete
                className={classes.job}
                label="Вид работ"
                placeholder="Проверка изоляции проводов"
                size="lg"
                w={903}
                lh={'24px'}
                limit={2}
                data={worktype!}
                value={work}
                onChange={setWork ? setWork : () => {}}
                disabled={disabled}
            />}
        </Stack>
    );
};

export default AnalysisInput;