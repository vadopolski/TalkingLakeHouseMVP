FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 5173

# Run development server (accessible from outside container)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
