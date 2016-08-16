/* ExemptionBrowser.jsx
**
** This is the root component for the Exemption Browser feature.
** It should provide a search field, a listing of search results, and the ability to
** see the details of a specific result.
*/

import React, { PropTypes } from 'react';

import ExemptionSearch from './ExemptionSearch';
import ExemptionList from './ExemptionList';

const ExemptionBrowser = ({exemptionQuery, exemptionResults, onQueryChange, onExemptionSearch}) => (
    <div className="exemptionBrowser">
        <ExemptionSearch query={exemptionQuery} onSubmit={onExemptionSearch} />
        <ExemptionList exemptions={exemptionResults} />
    </div>
);

ExemptionBrowser.propTypes = {
    exemptionQuery: PropTypes.string.isRequired,
    exemptionResults: PropTypes.array.isRequired,
    onExemptionSearch: PropTypes.func.isRequired,
};

export default ExemptionBrowser
