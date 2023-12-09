// src/components/Visualizations.tsx
import React, { useEffect } from 'react';
import { Card, CardContent, Typography, Box, LinearProgress, ImageList, ImageListItem, ImageListItemBar } from '@mui/material';
import Plot from 'react-plotly.js';
import { Experiment, InputData } from '../app/types';

interface ExperimentResult {
  input : {
    data: {
      name: string;
    }
    layout: {};
  };
  visualizations: {
    explainer : string;
    data: {
      data : {
        name: string;
        z: number[][];
      }
      layout: {};
    };
  }[];
}
interface VisualizationsProp {
    experimentResult: ExperimentResult[];
    predictions: any[];
    evaluations: any[];
    selectedImages: string[];
    selectedAlgorithms: string[];
}

const Visualizations: React.FC<VisualizationsProp> = ({ 
    experimentResult,
    predictions,
    evaluations,
    selectedImages,
    selectedAlgorithms,
  }) => {
  
  const results: ExperimentResult[] = JSON.parse(JSON.stringify(experimentResult));
  console.log(results);
  const algorithmList = ["Original", ...results[0].visualizations.map((visualization) => visualization.explainer)];
  return (
    <Box sx={{ mt: 4 }}>
      {results.map((result, index) => {
        const imagePrediction = predictions.find(pred => pred.image === result.input.data.name);
        const imageEvaluations = evaluations.filter((evaluation) => evaluation.image === result.input.data.name);

        return (
          <Box key={index} sx={{ marginBottom: 4, paddingBottom: 2, borderBottom: '2px solid #e0e0e0' }}>
            {/* Info Cards */}
            <Box sx={{ display: 'flex', justifyContent: 'space-around', marginBottom: 2 }}>
              {/* Label Card */}
              <Card sx={{ minWidth: 275 }}>
                <CardContent>
                  <Typography variant="h5" component="div">True Label</Typography>
                  <Typography variant="body2">{imagePrediction?.label}</Typography>
                </CardContent>
              </Card>

              {/* Probability Card */}
              <Card sx={{ minWidth: 275 }}>
                <CardContent>
                  <Typography variant="h5" component="div">Probabilities</Typography>
                  {imagePrediction?.probPredictions.map((probs: { label: string, score: number }, probIndex: number) => (
                    <Box key={probIndex} sx={{ mb: 1 }}>
                      <Typography variant="body2">{probs.label}: {Math.round(probs.score * 100)}%</Typography>
                      <LinearProgress variant="determinate" value={probs.score * 100} />
                    </Box>
                  ))}
                </CardContent>
              </Card>

              {/* Result Card */}
              <Card sx={{ minWidth: 275, bgcolor: imagePrediction?.isCorrect ? 'lightgreen' : 'red' }}>
                <CardContent>
                  <Typography variant="h5" component="div">{imagePrediction?.isCorrect ? 'Correct' : 'False'}</Typography>
                </CardContent>
              </Card>
            </Box>

            {/* Image Cards */}
            <ImageList sx={{ width: '100%', height: '300px' }} cols={algorithmList.length} rowHeight={164}>
              {algorithmList.map((algorithm, algIndex) => {
                const evaluation = imageEvaluations.find(evaluation => evaluation.algorithm === algorithm);

                return (
                  <ImageListItem key={algIndex} sx={{ width: '240px', minHeight: "300px" }}>
                    {algIndex === 0 ? (
                      <Box sx={{ p: 1}}>
                        <Plot 
                          data={result.input.data}
                          layout={result.input.layout}
                        />
                        <Typography variant="subtitle1" align="center">{algorithm}</Typography>
                      </Box>
                      ) : (
                        <Box sx={{ p: 1 }}>
                          {/* Should be replaced to multiple XAI algorithm result */}
                          <Plot 
                          data={result.visualizations.find(visualization => visualization.explainer === algorithm)?.data.data}
                          layout={result.visualizations.find(visualization => visualization.explainer === algorithm)?.data.layout}
                          />
                          <Typography variant="subtitle1" align="center">{algorithm}</Typography>
                          <Typography variant="body2" sx={{ textAlign: 'center' }}> Rank {algIndex}</Typography>
                          <Typography variant="body2" sx={{ textAlign: 'center' }}> Faithfulness ({evaluation?.evaluation.faithfulness})</Typography>
                          <Typography variant="body2" sx={{ textAlign: 'center' }}> Robustness ({evaluation?.evaluation.robustness})</Typography>
                        </Box>
                    )}
                  </ImageListItem>
                );
              })}
            </ImageList>
          </Box>
        );
      })}
    </Box>
  );
}

export default Visualizations;
