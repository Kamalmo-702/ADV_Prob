// Single source of truth for navigation: sidebar, home cards and routes all read this list.
export const MODULES = [
  { path: '/normal', label: 'Normal Distribution', issue: 2, summary: 'Probabilities and inverse values for any normal variable, with the shaded curve.' },
  { path: '/distributions', label: 't / χ² / F Explorer', issue: 2, summary: 'Change the degrees of freedom and see the curve, probabilities and critical values.' },
  { path: '/sampling', label: 'Sampling Distributions', issue: 3, summary: 'Sampling distribution of the mean, variance and proportion.' },
  { path: '/confidence-interval', label: 'Confidence Intervals', issue: 4, summary: 'Confidence interval for the mean with the right formula chosen for you.' },
  { path: '/sample-size', label: 'Sample Size', issue: 4, summary: 'How many observations you need for a given margin of error.' },
  { path: '/clt', label: 'CLT Simulator', issue: 5, summary: 'Watch sample means become bell-shaped as the sample size grows.' },
  { path: '/coverage', label: 'CI Coverage Demo', issue: 5, summary: 'See how many of 100 intervals really contain the true mean.' },
  { path: '/check-slides', label: 'Check the Slides', issue: 5, summary: 'Lecture answers compared with exact values.' },
]
