pipeline {
			agent any
			environment {
    			BRANCH_DEPLOY = "${env.BRANCH_NAME}"
    			ENVAWSACCOUNTID = "${BRANCH_DEPLOY}-AWS_ACCOUNT_ID"
    			ENVAWSREGISTRYURL = "${BRANCH_DEPLOY}-AWS_REGISTRY_URL"			} 
		  	stages {
		    	stage('build docker image') {
		    		when {
		            	anyOf { branch 'devops'; branch 'dev'; branch 'stage'; branch 'prod'; } 
		        	}
		      	steps {
		   	 		script {
		   	 			withCredentials([
            				string(credentialsId: ENVAWSACCOUNTID, variable: 'AWS_ACCOUNT_ID'),
            				string(credentialsId: ENVAWSREGISTRYURL, variable: 'AWS_REGISTRY_URL'),
            				string(credentialsId: 'AWS_DEFAULT_REGION', variable: 'AWS_DEFAULT_REGION')
            				])
          				 	{
   							sh '''
   								set +x
								localImageName="${AWS_REGISTRY_URL}:${BRANCH_DEPLOY}-${GIT_COMMIT}"
								docker build -t ${localImageName} .
							'''
							}
		      			}
					}
				}
				stage('publish docker image'){
					when {
		            	anyOf { branch 'devops'; branch 'dev'; branch 'stage'; branch 'prod'; } 
		        	}
					steps {
						script {
						withCredentials([
            				string(credentialsId: ENVAWSACCOUNTID, variable: 'AWS_ACCOUNT_ID'),
            				string(credentialsId: ENVAWSREGISTRYURL, variable: 'AWS_REGISTRY_URL'),
            				string(credentialsId: 'AWS_DEFAULT_REGION', variable: 'AWS_DEFAULT_REGION')
            				])
	    					{
			        		sh '''        			
					            docker_login=\$(aws ecr get-login --registry-ids ${AWS_ACCOUNT_ID} --no-include-email --region ${AWS_DEFAULT_REGION})
								login_result=\$(\$docker_login)
								localImageName="${AWS_REGISTRY_URL}:${BRANCH_DEPLOY}-${GIT_COMMIT}"
								latest_tag="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${AWS_REGISTRY_URL}:${BRANCH_DEPLOY}-latest"
								docker tag $localImageName \$latest_tag
								sha_tag="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${AWS_REGISTRY_URL}:${BRANCH_DEPLOY}-${GIT_COMMIT}"
								docker tag $localImageName \$sha_tag
								docker push \$latest_tag
								docker push \$sha_tag
							'''
							}
						}
					}	
				}

			}
		}
