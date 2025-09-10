import * as React from 'react';
import PropTypes from 'prop-types';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import CssBaseline from '@mui/material/CssBaseline';
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import MailIcon from '@mui/icons-material/Mail';
import MenuIcon from '@mui/icons-material/Menu';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import { Link, Routes, Route } from "react-router-dom";
import CalendarPage from '../pages/CalendarPage';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import LogoutIcon from '@mui/icons-material/Logout';
import { SignInPage } from '@toolpad/core/SignInPage';
import LoginPage from '../pages/LoginPage';
import UnauthenticatedRoute from '../privateRoutes/UnauthenticatedRoute';
import AuthenticatedRoute from '../privateRoutes/AuthenticatedRoute';
import UnauthorisedPage from '../pages/UnauthorisedPage';
import LogoutPage from '../pages/LogoutPage';
import AdminRoute from '../privateRoutes/AdminAuthRoute';
import GroupsPage from '../pages/GroupsPage';

const drawerWidth = 240;

function ResponsiveDrawer(props) {
  const { window } = props;
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [isClosing, setIsClosing] = React.useState(false);

  const handleDrawerClose = () => {
    setIsClosing(true);
    setMobileOpen(false);
  };

  const handleDrawerTransitionEnd = () => {
    setIsClosing(false);
  };

  const handleDrawerToggle = () => {
    if (!isClosing) {
      setMobileOpen(!mobileOpen);
    }
  };

  const drawer = (
    <div>
      {/* Logo in drawer header - replaces <Toolbar /> */}
      <Box sx={{ 
        height: 64, // Same height as Toolbar
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        px: 2 // padding horizontal
      }}>
        <img 
          src="assets/logo.png" 
          alt="Simplex Tuition Logo" 
          style={{ 
            height: 40, // Adjust as needed
            width: 'auto'
          }} 
        />
      </Box>
      <Divider />
      <List>
        <ListItem component={Link} to={"/groups"} key={"Groups"} disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <CalendarMonthIcon/>
              </ListItemIcon>
              <ListItemText primary={"Groups"} />
            </ListItemButton>
          </ListItem>
        <ListItem component={Link} to={"/calendar"} key={"Calendar"} disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <CalendarMonthIcon/>
              </ListItemIcon>
              <ListItemText primary={"Calendar"} />
            </ListItemButton>
          </ListItem>
      </List>
      <Divider />
      <List>
        <ListItem component={Link} to={"/logout"} key={"Logout"} disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <LogoutIcon/>
              </ListItemIcon>
              <ListItemText primary={"Logout"} />
            </ListItemButton>
          </ListItem>
      </List>
    </div>
  );

  // Remove this const when copying and pasting into your project.
  const container = window !== undefined ? () => window().document.body : undefined;

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            Simplex Tuition
          </Typography>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="mailbox folders"
      >
        {/* The implementation can be swapped with js to avoid SEO duplication of links. */}
        <Drawer
          container={container}
          variant="temporary"
          open={mobileOpen}
          onTransitionEnd={handleDrawerTransitionEnd}
          onClose={handleDrawerClose}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          slotProps={{
            root: {
              keepMounted: true, // Better open performance on mobile.
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` } }}
      >
        <Toolbar />
        <Routes>
          <Route path='/login' element={
            <UnauthenticatedRoute>
              <LoginPage/>
            </UnauthenticatedRoute>
            } />
          <Route path="/groups" element={
          <AuthenticatedRoute>
            <AdminRoute>
              <GroupsPage/>
            </AdminRoute>  
          </AuthenticatedRoute>
            } />
          {/* <Route path="/calendar" element={
            <AuthenticatedRoute>
              <AdminRoute>
                <CalendarPage/>
              </AdminRoute>  
            </AuthenticatedRoute>
            } /> */}
          <Route path="/unauthorised" element={
            <UnauthorisedPage/>
            } />
          <Route path="/logout" element={
            <LogoutPage/>
          } />
          <Route path="*" element={
            <AuthenticatedRoute>
              <AdminRoute>
                <h2>Welcome! Pick a section from the menu.</h2>
              </AdminRoute>
            </AuthenticatedRoute>
            } />
        </Routes>

      </Box>
    </Box>
  );
}

ResponsiveDrawer.propTypes = {
  /**
   * Injected by the documentation to work in an iframe.
   * Remove this when copying and pasting into your project.
   */
  window: PropTypes.func,
};

export default ResponsiveDrawer;
