# Railway Deployment Guide for LetterFlow

## Prerequisites
1. Railway account (https://railway.app)
2. Git repository with your code
3. PostgreSQL database (Railway provides this)

## Step 1: Connect Your Repository
1. Go to Railway dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect it's a Django app

## Step 2: Add PostgreSQL Database
1. In your project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically add the database environment variables

## Step 3: Set Environment Variables
In your Railway project settings, add these environment variables:

### Required Variables:
- `SECRET_KEY`: Generate a new secret key (use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DJANGO_SETTINGS_MODULE`: `letterflow.production`
- `RAILWAY_ENVIRONMENT`: `production`

### Optional Variables:
- `CUSTOM_DOMAIN`: Your custom domain if you have one
- `DEFAULT_FROM_EMAIL`: Email for system notifications

## Step 4: Deploy
1. Railway will automatically deploy when you push to your main branch
2. Monitor the build logs for any errors
3. The first deployment will fail because the database doesn't exist yet

## Step 5: Run Migrations
After the first deployment, you need to run migrations:

1. Go to your Railway project
2. Click on your web service
3. Go to "Variables" tab
4. Add a temporary variable: `RUN_MIGRATIONS=true`
5. Redeploy (this will trigger migrations)
6. Remove the `RUN_MIGRATIONS` variable after successful migration

## Step 6: Create Superuser
Create an admin user by running this command in Railway's terminal:

```bash
python manage.py createsuperuser
```

## Step 7: Verify Deployment
1. Check your app URL
2. Test the admin interface
3. Test user registration/login
4. Test core functionality

## Troubleshooting

### Common Issues:

1. **Database Connection Error**
   - Ensure PostgreSQL is added to your project
   - Check environment variables are set correctly

2. **Static Files Not Loading**
   - Verify `STATIC_ROOT` is set to `staticfiles`
   - Check that `collectstatic` runs during deployment

3. **Migration Errors**
   - Ensure database is properly connected
   - Check for any model conflicts

4. **Permission Errors**
   - Verify user roles and permissions are set up
   - Check middleware configuration

### Logs
- Check Railway logs in the dashboard
- Look for Django error messages
- Verify environment variables are loaded

## Security Checklist
- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is properly set
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] Database credentials are secure
- [ ] HTTPS is enabled (Railway provides this)

## Performance Tips
- Use Railway's built-in CDN for static files
- Enable database connection pooling
- Monitor resource usage in Railway dashboard
- Set appropriate worker processes in Procfile

## Support
If you encounter issues:
1. Check Railway documentation
2. Review Django deployment checklist
3. Check Railway community forums
4. Review your application logs
