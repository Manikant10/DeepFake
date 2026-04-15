export const extractErrorMessage = (error, fallback = 'Something went wrong. Please try again.') => {
  if (!error) return fallback;

  if (typeof error === 'string') {
    return error;
  }

  if (error.response?.data) {
    const { data } = error.response;
    if (typeof data === 'string') return data;
    if (typeof data?.detail === 'string') return data.detail;
    if (Array.isArray(data?.detail) && data.detail.length > 0) {
      const firstDetail = data.detail[0];
      if (typeof firstDetail?.msg === 'string') return firstDetail.msg;
    }
    if (typeof data?.message === 'string') return data.message;
    if (typeof data?.error === 'string') return data.error;
  }

  if (typeof error.message === 'string' && error.message.trim()) {
    return error.message;
  }

  return fallback;
};

export const extractErrorMessageFromResponse = async (response, fallback = 'Request failed. Please try again.') => {
  try {
    const payload = await response.clone().json();
    if (typeof payload === 'string') return payload;
    if (typeof payload?.detail === 'string') return payload.detail;
    if (Array.isArray(payload?.detail) && payload.detail.length > 0) {
      const firstDetail = payload.detail[0];
      if (typeof firstDetail?.msg === 'string') return firstDetail.msg;
    }
    if (typeof payload?.message === 'string') return payload.message;
    if (typeof payload?.error === 'string') return payload.error;
  } catch (jsonError) {
    try {
      const text = await response.clone().text();
      if (typeof text === 'string' && text.trim()) {
        return text.trim();
      }
    } catch (textError) {
      // No response body available.
    }
  }

  return fallback;
};

export const toSafeNumber = (value, fallback = 0) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};
