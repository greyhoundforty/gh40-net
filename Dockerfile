# Stage 1: Build the Astro project
FROM node:lts as builder

# Set the working directory
WORKDIR /app

# Copy over the package.json and package-lock.json
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install 

# Copy the rest of the application code
COPY . .

# Build the Astro project
RUN npm run build

# Stage 2: Serve the built Astro project using Nginx
FROM nginx:stable-alpine

# Copy the built Astro project from the previous stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 8080
EXPOSE 8080

# Update the Nginx configuration to listen on port 8080
RUN sed -i 's/listen\s*80;/listen 8080;/' /etc/nginx/conf.d/default.conf

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]

