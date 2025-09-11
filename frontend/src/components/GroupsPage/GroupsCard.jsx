import * as React from 'react';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Chip from '@mui/material/Chip';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PersonIcon from '@mui/icons-material/Person';
import SchoolIcon from '@mui/icons-material/School';
import { useNavigate } from 'react-router-dom';
import { formatDayAndTime } from '../../utils/helper';

export default function GroupsCard(props) {
  const navigate = useNavigate();
  const {
    id,
    lesson_length,
    associated_product,
    tutor,
    course,
    day_of_week,
    time_of_day,
    weekly_time,
    image_base64
  } = props;

  // Create a fallback image or use base64 if provided
  const imageSource = image_base64 
    ? `data:image/jpeg;base64,${image_base64}` 
    : "/static/images/cards/default-lesson.jpg";

  // Get tutor initials for avatar
  const getTutorInitials = (name) => {
    return name ? name.charAt(0).toUpperCase() : 'T';
  };
  console.log(props)
  return (
    <Card 
      sx={{ 
        width: "100%",
        borderRadius: 2,
        boxShadow: 2,
        '&:hover': {
          boxShadow: 4,
          transform: 'translateY(-2px)',
          transition: 'all 0.3s ease-in-out'
        }
      }}
    >
      <CardMedia
        component="img"
        alt={course || "Lesson image"}
        height="180"
        image={imageSource}
        sx={{
          objectFit: 'cover'
        }}
      />
      
      <CardContent sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 1 }}>
          <SchoolIcon color="primary" fontSize="small" />
          <Typography 
            gutterBottom 
            variant="h6" 
            component="div" 
            sx={{ 
              fontWeight: 600,
              mb: 0,
              color: 'text.primary'
            }}
          >
            {course || 'Course'}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 1 }}>
          <Avatar 
            sx={{ 
              width: 24, 
              height: 24, 
              fontSize: '0.75rem',
              bgcolor: 'primary.main'
            }}
          >
            {getTutorInitials(tutor)}
          </Avatar>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            Tutor: {tutor || 'TBA'}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 1 }}>
          <AccessTimeIcon color="action" fontSize="small" />
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            {
              formatDayAndTime(day_of_week, time_of_day)
            }
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
          <Chip 
            label={`${lesson_length || 0}h lesson`}
            size="small"
            variant="outlined"
            color="primary"
          />
          {associated_product && (
            <Chip 
              label={`${associated_product.name}`}
              size="small"
              variant="outlined"
              color="secondary"
            />
          )}
        </Box>
      </CardContent>

      <CardActions sx={{ pt: 0, px: 2, pb: 2 }}>
        <Button 
          size="small" 
          variant="contained"
          sx={{ 
            borderRadius: 2,
            textTransform: 'none',
            fontWeight: 500
          }}
          onClick={() => navigate(`explore/${id}`)}
        >
          Explore
        </Button>
        <Button 
          size="small"
          variant="outlined"
          sx={{ 
            borderRadius: 2,
            textTransform: 'none',
            fontWeight: 500
          }}
        >
          Start Lesson
        </Button>
      </CardActions>
    </Card>
  );
}