import { createStyles, Flex, Stack } from "@mantine/core";
import { observer } from "mobx-react-lite";

const useStyles = createStyles(() => ({
    mainWrapper: {
        padding:'24px',
    },
}));

type Props = {
    children?: React.ReactNode[];
};

const Wrapper = ({children}: Props) => {
    const { classes } = useStyles();

    return (
        <Flex justify="space-between" className={classes.mainWrapper} gap='1rem'>
            <Stack w={1139}>
                {children ? children[0] : <></>}
            </Stack>
            <Stack>
                {children ? children[1] : <></>}
            </Stack>
        </Flex>
    );
};

export default observer(Wrapper);