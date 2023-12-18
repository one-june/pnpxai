// src/features/apiService.tsx
import axios from 'axios';

interface ExperimentReq {
  inputs : number[];
  explainers: (number | undefined)[];
}

const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:${window.location.port}/api`;

export const fetchProjects = 
  () => axios.get(`${API_BASE_URL}/projects/`);

export const fetchModelsByProjectId = 
  (projectId: string) => axios.get(`${API_BASE_URL}/projects/${projectId}/models/`);

export const fetchInputsByExperimentId =
  (projectId: string, experimentId: string) => axios.get(`${API_BASE_URL}/projects/${projectId}/experiments/${experimentId}/inputs/`);

export const fetchExperiment =
  (projectId: string, experimentId: string, data: ExperimentReq) => axios.put(`${API_BASE_URL}/projects/${projectId}/experiments/${experimentId}/`, data);

