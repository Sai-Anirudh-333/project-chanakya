# Use official lightweight Node.js image
FROM node:20-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy the rest of the frontend code and build the Next.js app
COPY . .
RUN npm run build

# Use a pristine, lightweight runner for production
FROM node:20-alpine AS runner
WORKDIR /app

# Copy the built assets from the builder stage
COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

# Expose the Next.js port
EXPOSE 3000

# Start the Next.js production server
CMD ["npm", "start"]
