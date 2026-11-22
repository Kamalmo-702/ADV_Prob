import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Home from './pages/Home.jsx'
import NormalDistribution from './pages/NormalDistribution.jsx'
import DistributionsExplorer from './pages/DistributionsExplorer.jsx'
import SamplingDistributions from './pages/SamplingDistributions.jsx'
import ConfidenceInterval from './pages/ConfidenceInterval.jsx'
import SampleSize from './pages/SampleSize.jsx'
import CLTSimulator from './pages/CLTSimulator.jsx'
import CICoverage from './pages/CICoverage.jsx'
import CheckSlides from './pages/CheckSlides.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="normal" element={<NormalDistribution />} />
        <Route path="distributions" element={<DistributionsExplorer />} />
        <Route path="sampling" element={<SamplingDistributions />} />
        <Route path="confidence-interval" element={<ConfidenceInterval />} />
        <Route path="sample-size" element={<SampleSize />} />
        <Route path="clt" element={<CLTSimulator />} />
        <Route path="coverage" element={<CICoverage />} />
        <Route path="check-slides" element={<CheckSlides />} />
      </Route>
    </Routes>
  )
}
