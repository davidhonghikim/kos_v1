FROM node:18-alpine

WORKDIR /app
COPY frontend /app
RUN npm install && npm run build

CMD ["npm", "run", "dev"]
