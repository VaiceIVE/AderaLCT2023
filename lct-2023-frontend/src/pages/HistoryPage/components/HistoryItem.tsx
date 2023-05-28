import { createStyles, Stack } from "@mantine/core";
import { IAnalysis } from "../../../models/IAnalysis";
import ItemFooter from "./ItemFooter";
import ItemHeading from "./ItemHeading";

const useStyles = createStyles(() => ({

    wrapper: {
        border: '1px solid #E9ECEF',
        borderRadius: '16px',
        padding: '23px'
    },
}));

const HistoryItem = ({type, date, id, criterias}: IAnalysis) => {
    const { classes } = useStyles();

    return (
        <Stack className={classes.wrapper} spacing={16}>
            <ItemHeading type={type!} date={date!}/>
            <ItemFooter criterias={criterias!} type={type!} id={id!}/>
        </Stack>
    );
};

export default HistoryItem;