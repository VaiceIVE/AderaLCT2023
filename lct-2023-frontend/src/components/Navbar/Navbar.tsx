import { Navbar, createStyles } from '@mantine/core';
import NavbarHeader from './NavbarHeader';
import NavbarHelp from './NavbarHelp';
import NavbarLinksGroup from './NavbarLinksGroup';


const useStyles = createStyles(() => ({
    navbar: {
        borderRight: '1px solid #E9ECEF', 
        position: 'sticky',
        top: 0,
        zIndex: 10000
    },

    header: {
        padding: '56px 23px 23px 24px',
        borderBottom: '1px solid #E9ECEF',
    },

    links: {
        padding: '32px 23px 31px 24px',
        borderBottom: '1px solid #E9ECEF'
    },

    footer: {
        padding: '24px 23px 32px 24px'
    },
}));

const NavbarNested = () => {
    const { classes } = useStyles();

    return (
        <Navbar 
            width={{ base: '348px' }}  
            className={classes.navbar}
            height={'100vh'} 
        >
            <Navbar.Section className={classes.header}>
                <NavbarHeader/>
            </Navbar.Section>

            <Navbar.Section grow className={classes.links}>
                <NavbarLinksGroup/>
            </Navbar.Section>

            <Navbar.Section className={classes.footer}>
                <NavbarHelp/>
            </Navbar.Section>
        </Navbar>
    );
};

export default NavbarNested;