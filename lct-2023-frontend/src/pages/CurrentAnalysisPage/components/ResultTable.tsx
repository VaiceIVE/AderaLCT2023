import { useContext, useMemo } from 'react';
import { MantineReactTable, MRT_ColumnDef } from 'mantine-react-table';
import { Box, Button, Flex, List, MantineProvider, Tooltip, useMantineTheme } from '@mantine/core';
import { IconArrowsMaximize, IconEdit, IconTrashX } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { MAPS_ROUTE } from '../../../utils/const';
import { Context } from '../../../main';
import { observer } from 'mobx-react-lite';

type IAnalysisResult = {
    workname: string[];
    adress: string;
    priority: string;
    causes: string[];
};

const Example = (props: 
    {result: IAnalysisResult[], handleAdressDelete: Function, 
        open: () => void, handleSetWorks: Function, handleModalOpen: Function}) => {
    const theme = useMantineTheme();
    const navigate = useNavigate();
    const { MStore } = useContext(Context);

    const handleEditClick = (workname: string[], adress: string) => {
        props.handleSetWorks(workname, adress);
        props.open();
    };

    const columns = useMemo<MRT_ColumnDef<IAnalysisResult>[]>(
        () => [
            {
                accessorKey: 'adress',
                id: 'adress', 
                header: 'Адрес объекта',
            },
            {
                accessorKey: 'causes', 
                header: 'Характеристика',
                size: 100,
                Cell: ({ cell }) => (
                    <>
                    {!cell.getValue<string[]>() ? 
                        <Box
                            sx={(theme) => ({
                                background: theme.colors.gray[9],
                                borderRadius: '16px',
                                color: '#fff',
                                padding: '4px 12px',
                                display: 'inline-block',
                                cursor: 'pointer'
                            })}
                        >
                            Плановая работа
                        </Box>
                    :
                    <Tooltip label={!cell.getValue<string[]>().indexOf('МосГаз') ? 
                        cell.getValue<string[]>().indexOf('Авария') ? 'МосГаз, Аварийность' : 'МосГаз'
                        : !cell.getValue<string[]>().indexOf('Авария') ? 'Аварийность' : undefined}
                        disabled={cell.getValue<string[]>().length === 0}
                    >
                        <Box
                            sx={(theme) => ({
                                background: cell.getValue<string[]>().length != 0 
                                ? theme.colors.red[7] : theme.colors.gray[9],
                                borderRadius: '16px',
                                color: '#fff',
                                padding: '4px 12px',
                                display: 'inline-block',
                                cursor: 'pointer'
                            })}
                        >
                            {cell.getValue<string[]>().length === 0 ? 'Плановая работа' : 'Срочная работа'}
                        </Box>
                    </Tooltip>}
                    </>
                ),
            },
            {
                accessorKey: 'workname',
                header: 'Рекомендуемые работы',
                Cell: ({ cell }) => (
                    <List
                        size="sm"
                        sx={(_theme) => ({
                            fontSize: '16px'
                        })}
                    >
                        {cell.getValue<string[]>().map((item) => (
                            <List.Item key={item}>{item}</List.Item>
                        ))}
                    </List>
                ),
            },
        ],
        [],
    );
    
    return (
        <MantineProvider
            theme={{
                primaryColor: 'red',
            }}
        >
        <MantineReactTable
            initialState={{ showColumnFilters: true, showGlobalFilter: true, }}
            enableGlobalFilterModes={false}
            enableFilterMatchHighlighting
            enableGlobalFilterRankedResults={false}
            columns={columns}
            data={props.result}
            enableColumnOrdering
            enablePinning
            enableRowActions
            enableRowSelection
            enableColumnActions={false}
            enableColumnDragging={false}
            enableToolbarInternalActions={false}
            positionToolbarAlertBanner="none"
            mantineTableBodyProps={{
                sx: {
                    '& td:nth-of-type(n)': {
                        padding: '24px 16px',
                        fontSize: '16px',
                        lineHeight: '24px',
                        color: '#212529'
                    },
                },
            }}
            mantineTableHeadProps={{
                sx: {
                    '& th:nth-of-type(n)': {
                        padding: '24px 16px 23px',
                        fontSize: '16px',
                        lineHeight: '22px',
                        color: '#212529',

                        'input[type=text]': {
                            marginTop: '8px',
                            height: '31px'
                        }
                    },
                }
            }}
            mantineTopToolbarProps={{
                sx: {
                    padding: '8px'
                }
            }}
            mantineSelectAllCheckboxProps={{
                color: 'red.7',
                sx: {
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }
            }}
            mantinePaperProps={{
                sx: {
                    borderRadius: '8px',
                    boxShadow: 'none',
                    border: '1px solid #E9ECEF',
                },
            }}
            renderTopToolbarCustomActions={({ table }) => {
    
                const handleActivate = () => {
                    MStore.mapsClear();
                    table.getSelectedRowModel().flatRows.map((row) => {
                        MStore.setAddresses(row.getValue('adress'));
                        MStore.setCauses(row.getValue('causes'));
                        MStore.setWorkname(row.getValue('workname'));
                    });
                    navigate(MAPS_ROUTE);
                };
                
                return (
                        <Button
                            fz='lg'
                            w={212} h={48}
                            fw={400}
                            style={table.getSelectedRowModel().rows.length === 0 ?
                                {color: '#1C1C10C', background: '#E9ECEF', 
                                border: '1px solid #ADB5BD', cursor: 'pointer'} :
                                {color: '#1C1C1C', background: 'white', 
                                border: '1px solid #ADB5BD', cursor: 'pointer'}
                            }
                            onClick={handleActivate}
                            disabled={table.getSelectedRowModel().rows.length === 0}
                        >
                            Смотреть на карте
                        </Button>
                );
            }}

            renderRowActions={({cell}) => {
                return (
                    <Flex gap={10} align="center">
                        <IconArrowsMaximize
                            onClick={() => 
                                props.handleModalOpen(cell.row._valuesCache.adress)}
                            style={{cursor: 'pointer'}} 
                            stroke={'2'} 
                            color={theme.colors.gray[9]}/>
                        <IconEdit
                            onClick={() =>
                                handleEditClick(cell.row._valuesCache.workname, cell.row._valuesCache.adress)}
                            style={{cursor: 'pointer'}} 
                            stroke={'2'} 
                            color={theme.colors.gray[9]}/>
                        <IconTrashX
                            onClick={() => props.handleAdressDelete(cell.row._valuesCache.adress)}
                            style={{cursor: 'pointer'}} 
                            stroke={'2'} 
                            color={theme.colors.red[7]}/>
                    </Flex>
                );
            }}
        />
        </MantineProvider>
    );
};

export default observer(Example);