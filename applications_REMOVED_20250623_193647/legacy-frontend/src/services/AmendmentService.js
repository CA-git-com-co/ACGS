import api from './api'; // Import the central API instance

const API_URL_PREFIX = process.env.REACT_APP_AC_API_URL || 'http://localhost:8001/api/v1';

const getConstitutionalPrinciples = async () => {
  try {
    const response = await api.get(`${API_URL_PREFIX}/constitutional-principles/`);
    return response.data;
  } catch (error) {
    console.error(
      'Failed to fetch constitutional principles:',
      error.response ? error.response.data : error.message
    );
    throw error.response
      ? error.response.data
      : new Error('Failed to fetch constitutional principles');
  }
};

const submitAmendmentProposal = async (amendmentData) => {
  try {
    const response = await api.post(`${API_URL_PREFIX}/constitutional-amendments/`, amendmentData);
    return response.data;
  } catch (error) {
    console.error(
      'Failed to submit amendment proposal:',
      error.response ? error.response.data : error.message
    );
    throw error.response ? error.response.data : new Error('Failed to submit amendment proposal');
  }
};

const getAmendmentProposals = async (status = null) => {
  try {
    const params = {};
    if (status) {
      params.status = status;
    }
    const response = await api.get(`${API_URL_PREFIX}/constitutional-amendments/`, { params });
    return response.data;
  } catch (error) {
    console.error(
      'Failed to fetch amendment proposals:',
      error.response ? error.response.data : error.message
    );
    throw error.response ? error.response.data : new Error('Failed to fetch amendment proposals');
  }
};

const castAmendmentVote = async (amendmentId, voteData) => {
  try {
    const response = await api.post(
      `${API_URL_PREFIX}/constitutional-amendments/${amendmentId}/vote`,
      voteData
    );
    return response.data;
  } catch (error) {
    console.error(
      'Failed to cast amendment vote:',
      error.response ? error.response.data : error.message
    );
    throw error.response ? error.response.data : new Error('Failed to cast amendment vote');
  }
};

const getAmendmentVotes = async (amendmentId) => {
  try {
    const response = await api.get(
      `${API_URL_PREFIX}/constitutional-amendments/${amendmentId}/votes`
    );
    return response.data;
  } catch (error) {
    console.error(
      'Failed to fetch amendment votes:',
      error.response ? error.response.data : error.message
    );
    throw error.response ? error.response.data : new Error('Failed to fetch amendment votes');
  }
};

const AmendmentService = {
  getConstitutionalPrinciples,
  submitAmendmentProposal,
  getAmendmentProposals,
  castAmendmentVote,
  getAmendmentVotes,
};

export default AmendmentService;
