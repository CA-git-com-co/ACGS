import api from './api'; // Import the central API instance

const API_URL_PREFIX = process.env.REACT_APP_GS_API_URL || 'http://localhost:8003/api/v1';

const synthesizePolicies = async (synthesisRequestData) => {
    try {
        const response = await api.post(`${API_URL_PREFIX}/synthesize/`, synthesisRequestData);
        return response.data;
    } catch (error) {
        console.error('Failed to synthesize policies:', error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Failed to synthesize policies');
    }
};

const analyzeAmendmentImpact = async (amendmentData) => {
    try {
        const response = await api.post(`${API_URL_PREFIX}/analyze-amendment-impact/`, amendmentData);
        return response.data;
    } catch (error) {
        console.error('Failed to analyze amendment impact:', error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Failed to analyze amendment impact');
    }
};

const validateSemanticConsistency = async (validationData) => {
    try {
        const response = await api.post(`${API_URL_PREFIX}/validate-semantic-consistency/`, validationData);
        return response.data;
    } catch (error) {
        console.error('Failed to validate semantic consistency:', error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Failed to validate semantic consistency');
    }
};

const detectPolicyConflicts = async (conflictData) => {
    try {
        const response = await api.post(`${API_URL_PREFIX}/detect-policy-conflicts/`, conflictData);
        return response.data;
    } catch (error) {
        console.error('Failed to detect policy conflicts:', error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Failed to detect policy conflicts');
    }
};

const GSService = {
    synthesizePolicies,
    analyzeAmendmentImpact,
    validateSemanticConsistency,
    detectPolicyConflicts
};

export default GSService;