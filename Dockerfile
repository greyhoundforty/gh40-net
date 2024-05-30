# Stage 1: Build the Astro project
FROM node:lts as builder

# Set the working directory
WORKDIR /app

# Copy over the package.json and package-lock.json
COPY package.json package-lock.json./

# Install dependencies
RUN npm ci

# Copy the rest of the application code
COPY . .

# Build the Astro project
RUN npm run build

# Stage 2: Serve the built project with Nginx
FROM nginx:alpine as runner

# Copy the built files from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80 for the web server
EXPOSE 80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]
