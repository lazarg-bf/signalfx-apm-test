FROM node:18-slim

# Create a non-root user with UID 1000 and group

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy app source
COPY . .

# Set environment variables
ENV NODE_ENV=production
ENV PORT=8080
ENV OTEL_SERVICE_NAME=apmtest-nodejs

# Give ownership to the non-root user
RUN chown -R 1000:1000 /app

# Switch to the non-root user
USER 1000

EXPOSE 8080

# Use the npm script which runs:
# node -r @splunk/otel/instrument nodejs_app.js
CMD [ "npm", "start" ]
