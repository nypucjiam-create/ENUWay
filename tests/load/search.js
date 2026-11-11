import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 30,
  duration: '3m',
  thresholds: {
    http_req_duration: ['p(95)<800'], // NFT-PERF-01
    http_req_failed: ['rate<0.01'],   // NFT-REL-01
  },
};

export default function () {
  const response = http.get(
    `${__ENV.BASE_URL || 'http://localhost:8000'}/api/rides?destination=%D0%95%D2%B0%D0%A3`,
  );
  check(response, {
    'HTTP 200': (result) => result.status === 200,
    'жауап массив түрінде': (result) => Array.isArray(result.json()),
  });
}

